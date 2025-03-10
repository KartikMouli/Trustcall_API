from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from django.core.cache import cache
from django.db.models import Q
from .models import SpamRecord, GlobalPhonebook, SpamReport, User, Contact
from .serializers import UserSerializer, ContactSerializer, GlobalPhonebookSerializer, SpamReportSerializer
from rest_framework.throttling import UserRateThrottle

# Custom Throttling class
class CustomUserRateThrottle(UserRateThrottle):
    rate = '10/minute'  # Limit the user to 10 requests per minute

def calculate_spam_likelihood(spam_count):
    total_spam_records = SpamRecord.objects.count()
    max_threshold = total_spam_records * 0.1  # 10% of total spam records
    likelihood = (spam_count / max_threshold) * 100
    return min(100, likelihood)

# User Registration
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """
    Register a new user and add to the Global Phonebook.
    """
    if request.method == "POST":
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Add user to GlobalPhonebook
            global_entry, created = GlobalPhonebook.objects.get_or_create(
                phone_number=user.phone_number,
                defaults={"name": user.username, "is_spam": False},
            )

            if created:
                print(f"User {user.username} added to GlobalPhonebook.")

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Add Contact
@api_view(["POST"])
def add_contact(request):
    """
    Add a contact for the authenticated user and update the global phonebook.
    """
    if request.user.is_authenticated:
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save(user=request.user)

            # Add or update the global phonebook
            global_entry, created = GlobalPhonebook.objects.get_or_create(
                phone_number=contact.phone_number,
                defaults={"name": contact.name, "is_spam": False},
            )

            if not created:
                global_entry.name = contact.name
                global_entry.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

# Mark Spam
@api_view(["POST"])
def mark_spam(request):
    """
    Mark a phone number as spam. Only authenticated users can report spam.
    """
    if request.user.is_authenticated:
        phone_number = request.data.get("phone_number")

        # Ensure the user has not already reported this number as spam
        if SpamReport.objects.filter(user=request.user, phone_number=phone_number).exists():
            return Response({"error": "You have already reported this number as spam."}, status=status.HTTP_400_BAD_REQUEST)

        # Create spam report and update spam record
        spam_data = {"user": request.user.id, "phone_number": phone_number}
        serializer = SpamReportSerializer(data=spam_data)
        if serializer.is_valid():
            serializer.save()

            # Increment spam count in SpamRecord
            spam_record, created = SpamRecord.objects.get_or_create(phone_number=phone_number)
            spam_record.spam_count += 1
            spam_record.save()

            # Update global phonebook entry to mark as spam
            global_entry, created = GlobalPhonebook.objects.get_or_create(phone_number=phone_number)
            global_entry.is_spam = True
            global_entry.save()

            return Response({"message": "Spam reported successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

# Search by Name
@api_view(["GET"])
@throttle_classes([CustomUserRateThrottle])
def search_by_name(request):
    """
    Search for a person by name in the global phonebook.
    """
    if request.user.is_authenticated:
        query = request.GET.get("query", "").strip()
        if not query:
            return Response({"error": "Query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"search_{query}"
        cached_results = cache.get(cache_key)

        if cached_results:
            return Response(cached_results, status=status.HTTP_200_OK)

        starts_with_results = GlobalPhonebook.objects.filter(name__istartswith=query)
        contains_results = GlobalPhonebook.objects.filter(name__icontains=query).exclude(name__istartswith=query)
        results = list(starts_with_results) + list(contains_results)

        # Prepare response data with spam likelihood
        data = []
        for result in results:
            spam_record = SpamRecord.objects.filter(phone_number=result.phone_number).first()
            spam_likelihood = calculate_spam_likelihood(spam_record.spam_count if spam_record else 0)

            data.append({
                "name": result.name,
                "phone_number": result.phone_number,
                "spam_likelihood": spam_likelihood,
            })

        cache.set(cache_key, data, timeout=300)

        return Response(data, status=status.HTTP_200_OK)

    return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

# Search by Phone Number
@api_view(["GET"])
@throttle_classes([CustomUserRateThrottle])
def search_by_phone(request):
    """
    Search for a phone number in the global phonebook.
    """
    if request.user.is_authenticated:
        query = request.GET.get("query", "").strip()
        print(query)
        if not query:
            return Response({"error": "Query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"search_{query}"
        cached_results = cache.get(cache_key)

        if cached_results:
            return Response(cached_results, status=status.HTTP_200_OK)

        # Search for a registered user first
        registered_user = User.objects.filter(phone_number=query).first()
        if registered_user:
            spam_count = SpamRecord.objects.filter(phone_number=query).first()
            spam_likelihood = calculate_spam_likelihood(spam_count.spam_count if spam_count else 0)
            data = {
                "name": registered_user.username,
                "phone_number": registered_user.phone_number,
                "spam_likelihood": spam_likelihood,
                "email": registered_user.email_address,
            }
            cache.set(cache_key, data, timeout=300)  # Cache for 5 minutes
            return Response(data, status=status.HTTP_200_OK)

        # If no registered user, search in GlobalPhonebook
        results = GlobalPhonebook.objects.filter(phone_number=query)
        data = []
        for result in results:
            spam_count = SpamRecord.objects.filter(phone_number=result.phone_number).first()
            spam_likelihood = calculate_spam_likelihood(spam_count.spam_count if spam_count else 0)
            data.append({
                "name": result.name,
                "phone_number": result.phone_number,
                "spam_likelihood": spam_likelihood,
            })

        cache.set(cache_key, data, timeout=300)  

        return Response(data, status=status.HTTP_200_OK)

    return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
