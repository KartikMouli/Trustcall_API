from django.db import models
from django.contrib.auth.models import AbstractUser
import phonenumbers


class User(AbstractUser):
    """
    Custom User model with a phone number field and email address.
    """
    phone_number = models.CharField(max_length=15, unique=True, db_index=True)
    email = models.EmailField(null=True, blank=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username


class Contact(models.Model):
    """
    Model representing a user's contact with phone number validation.
    """
    owner  = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts")
    phone_number = models.CharField(max_length=15,db_index=True)
    name = models.CharField(max_length=100)


    def __str__(self):
        return f"{self.name} ({self.phone_number})"




class SpamReport(models.Model):
    """
    Model for tracking spam reports by users for specific phone numbers.
    """
    phone_number = models.CharField(max_length=15)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reporter', 'phone_number')
        indexes = [
            models.Index(fields=['reporter', 'phone_number']),
        ]

    def __str__(self):
        return f"User {self.username} reported {self.phone_number} as spam"
