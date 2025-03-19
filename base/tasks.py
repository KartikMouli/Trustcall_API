from celery import shared_task
from .models import SpamReport, Contact
import csv
import os
from django.core.cache import cache


@shared_task
def recalculate_spam_likelihood(phone_number):
    """
    Recalculate the spam likelihood for a given phone number.
    """
    spam_count = SpamReport.objects.filter(phone_number=phone_number).count()
    total_reports = SpamReport.objects.count()

    if total_reports == 0:
        likelihood = 0
    else:
        likelihood = (spam_count / total_reports) * 100

    # Cache the result to avoid repeated calculations
    cache_key = f"spam_likelihood_{phone_number}"
    cache.set(cache_key, round(likelihood, 2), timeout=3600)  # Cache for 1 hour

    return round(likelihood, 2)



@shared_task
def export_contacts_task(user_id):
    """
    Export all contacts of a user to a CSV file.
    """
    contacts = Contact.objects.filter(owner_id=user_id)
    persistent_dir = "/persistent_storage/"
    os.makedirs(persistent_dir, exist_ok=True)  # Ensure directory exists

    file_path = os.path.join(persistent_dir, f"contacts_user_{user_id}.csv")

    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Phone Number'])  # Header row
        for contact in contacts:
            writer.writerow([contact.name, contact.phone_number])

    return file_path  # Return the path of the generated file