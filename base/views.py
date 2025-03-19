from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from django.core.cache import cache
from django.db.models import Q
from .models import SpamReport, User, Contact
from .serializers import UserSerializer, ContactSerializer
from rest_framework.throttling import UserRateThrottle


# Custom Throttling class
class CustomUserRateThrottle(UserRateThrottle):
    rate = "1000/minute"


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
    print("data:",request)
    serializer = ContactSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Mark Spam
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
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
        return Response(
            {"error": "Query parameter is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cache_key = f"search_name_{query.lower()}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return Response(cached_data)

    # Users whose names start with query (priority)
    users_startswith = User.objects.filter(username__istartswith=query)
    contacts_startswith = Contact.objects.filter(name__istartswith=query)

    # Users whose names contain query but don't start with it (lower priority)
    users_contains = User.objects.filter(username__icontains=query).exclude(
        id__in=users_startswith
    )
    contacts_contains = Contact.objects.filter(name__icontains=query).exclude(
        id__in=contacts_startswith
    )

    results = []

    # Combine and serialize results with spam likelihood
    for user in list(users_startswith) + list(users_contains):
        results.append(
            {
                "name": user.username,
                "phone_number": user.phone_number,
                "spam_likelihood": calculate_spam_likelihood(user.phone_number),
                "is_registered_user": True,
            }
        )

    for contact in list(contacts_startswith) + list(contacts_contains):
        results.append(
            {
                "name": contact.name,
                "phone_number": contact.phone_number,
                "spam_likelihood": calculate_spam_likelihood(contact.phone_number),
                "is_registered_user": False,
            }
        )

    cache.set(cache_key, results, timeout=300)  # Cache for 5 minutes

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
