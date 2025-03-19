from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from django.core.cache import cache
from .models import SpamReport, User, Contact
from .serializers import UserSerializer, ContactSerializer
from rest_framework.throttling import UserRateThrottle
from django.db.models import Case, When, IntegerField, Q
from django.db.models.functions import TruncDay
from django.db.models import Count

# Custom Throttling class
class CustomUserRateThrottle(UserRateThrottle):
    rate = "10/minute"


def calculate_spam_likelihood(phone_number):
    spam_count = SpamReport.objects.filter(phone_number=phone_number).count()
    total_reports = SpamReport.objects.count()
    if total_reports == 0:
        return 0
    likelihood = (spam_count / total_reports) * 100
    return min(100, round(likelihood, 2))


# User Registration
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """
    Register a new user and add to the Global Phonebook.
    """

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Add Contact
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def add_contact(request):
    """
    Add a contact for the authenticated user and update the global phonebook.
    """
    serializer = ContactSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save(owner=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Mark Spam
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([CustomUserRateThrottle])
def mark_spam(request):
    """
    Mark a phone number as spam. Only authenticated users can report spam.
    """
    phone_number = request.data.get("phone_number")
    if not phone_number:
        return Response(
            {"error": "phone_number is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    # Avoid duplicate spam reports by same user
    if SpamReport.objects.filter(
        reporter=request.user, phone_number=phone_number
    ).exists():
        return Response(
            {"error": "You have already reported this number as spam."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    SpamReport.objects.create(reporter=request.user, phone_number=phone_number)
    return Response(
        {"message": "Spam reported successfully."}, status=status.HTTP_201_CREATED
    )


# Search by Name View (Global Phonebook: Users + Contacts)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([CustomUserRateThrottle])
def search_by_name(request):
    query = request.GET.get("query", "").strip()
    if not query:
        return Response({"error": "Query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    cache_key = f"search_name_{query.lower()}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)
    
    
    user_qs = User.objects.filter(Q(username__icontains=query))
    user_qs = user_qs.annotate(
        priority=Case(
            When(username__istartswith=query, then=0),
            default=1,
            output_field=IntegerField(),
        )
    ).order_by('priority', 'username')
    
    contact_qs = Contact.objects.filter(Q(name__icontains=query))
    contact_qs = contact_qs.annotate(
        priority=Case(
            When(name__istartswith=query, then=0),
            default=1,
            output_field=IntegerField(),
        )
    ).order_by('priority', 'name')
    
    # Serialize results
    results = []
    
    for user in user_qs:
        results.append({
            "name": user.username,
            "phone_number": user.phone_number,
            "spam_likelihood": calculate_spam_likelihood(user.phone_number),
            "is_registered_user": True,
        })
    
    for contact in contact_qs:
        results.append({
            "name": contact.name,
            "phone_number": contact.phone_number,
            "spam_likelihood": calculate_spam_likelihood(contact.phone_number),
            "is_registered_user": False,
        })
    
    # Optionally apply pagination here
    cache.set(cache_key, results, timeout=300)
    return Response(results)



# Search by Phone Number View (Global Phonebook: Users + Contacts)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([CustomUserRateThrottle])
def search_by_phone(request):
    phone_query = request.GET.get("query", "").strip()
    if not phone_query:
        return Response(
            {"error": "Query parameter is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cache_key = f"search_phone_{phone_query}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

    user = User.objects.filter(phone_number=phone_query).first()

    if user:
        data = {
            "name": user.username,
            "phone_number": user.phone_number,
            "spam_likelihood": calculate_spam_likelihood(user.phone_number),
            "email": None,
            "is_registered_user": True,
        }
        # Email visible only if searching user is in user's contacts
        if Contact.objects.filter(
            owner=user, phone_number=request.user.phone_number
        ).exists():
            data["email"] = user.email

        cache.set(cache_key, data, timeout=300)
        return Response(data)

    # If no registered user found, look into contacts globally
    contacts = Contact.objects.filter(phone_number=phone_query).distinct(
        "name", "phone_number"
    )

    results = []

    for contact in contacts:
        results.append(
            {
                "name": contact.name,
                "phone_number": contact.phone_number,
                "spam_likelihood": calculate_spam_likelihood(contact.phone_number),
                "email": None,
                "is_registered_user": False,
            }
        )

    cache.set(cache_key, results, timeout=300)

    return Response(results)


# Detail view for a specific phone number (optional but recommended)
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([CustomUserRateThrottle])
def person_detail(request, phone_number):

    user = User.objects.filter(phone_number=phone_number).first()

    data = {
        "name": None,
        "phone_number": phone_number,
        "spam_likelihood": calculate_spam_likelihood(phone_number),
        "email": None,
        "is_registered_user": False,
    }

    if user:
        data["name"] = user.username
        data["is_registered_user"] = True

        # Email visible only if searching user is in user's contacts
        if Contact.objects.filter(
            owner=user, phone_number=request.user.phone_number
        ).exists():
            data["email"] = user.email

    else:
        contact_entry = Contact.objects.filter(phone_number=phone_number).first()
        if contact_entry:
            data["name"] = contact_entry.name

    return Response(data)

from django.http import HttpResponse
import csv

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@throttle_classes([CustomUserRateThrottle])
def export_contacts_csv(request):
    """
    Exports the authenticated user's contacts as a CSV file.
    """
    contacts = request.user.contacts.all()  # Assuming a related name 'contacts'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="contacts.csv"'
    
    writer = csv.writer(response)
    # Write header row
    writer.writerow(['Name', 'Phone Number'])
    
    # Write data rows
    for contact in contacts:
        writer.writerow([contact.name, contact.phone_number])
    
    return response


from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import api_view, permission_classes, parser_classes
import io

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser])
def import_contacts_csv(request):
    """
    Imports contacts from a CSV file uploaded by the user.
    CSV file should have headers: Name, Phone Number, Email.
    """
    file_obj = request.FILES.get('file', None)
    if not file_obj:
        return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        decoded_file = file_obj.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
    except Exception as e:
        return Response({'error': 'Failed to read CSV file.'}, status=status.HTTP_400_BAD_REQUEST)
    
    contacts_created = 0
    for row in reader:
        name = row.get('Name')
        phone_number = row.get('Phone Number')

        if not name or not phone_number:
            continue  # Skip invalid rows
        
        # Create or update the contact
        contact, created = Contact.objects.update_or_create(
            owner=request.user,
            phone_number=phone_number,
            defaults={'name': name},
        )
        if created:
            contacts_created += 1

    return Response({'message': f'{contacts_created} contacts imported successfully.'})





@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def analytics_top_spam_numbers(request):
    """
    Return the top spam reported numbers based on the count of reports.
    """
    limit = request.GET.get('limit', 10)
    try:
        limit = int(limit)
    except ValueError:
        limit = 10

    # Aggregate spam reports by phone number and annotate with the report count.
    spam_data = (
        SpamReport.objects
        .values('phone_number')
        .annotate(report_count=Count('phone_number'))
        .order_by('-report_count')[:limit]
    )

    return Response(spam_data, status=status.HTTP_200_OK)




@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def analytics_spam_trends(request):
    """
    Return daily spam report counts for trend analysis.
    """
    trend_data = (
        SpamReport.objects
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(report_count=Count('id'))
        .order_by('day')
    )
    return Response(trend_data, status=status.HTTP_200_OK)
