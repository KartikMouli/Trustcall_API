from django.db import models
from django.contrib.auth.models import AbstractUser
import phonenumbers


class User(AbstractUser):
    """
    Custom User model with a phone number field and email address.
    """
    phone_number = models.CharField(max_length=15, unique=True)
    email_address = models.EmailField(null=True, blank=True)

    def clean(self):
        """
        Validate phone number format using phonenumbers library.
        """
        try:
            parsed_phone = phonenumbers.parse(self.phone_number, "IN")
            if not phonenumbers.is_valid_number(parsed_phone):
                raise ValueError("Invalid phone number")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError("Invalid phone number format")

    def save(self, *args, **kwargs):
        """
        Clean the phone number before saving.
        """
        self.clean()
        super().save(*args, **kwargs)    

    def __str__(self):
        return self.username


class Contact(models.Model):
    """
    Model representing a user's contact with phone number validation.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts")
    phone_number = models.CharField(max_length=15)
    name = models.CharField(max_length=255)

    class Meta:
        indexes = [
            models.Index(fields=['phone_number']),
        ]

    def clean(self):
        """
        Validate phone number format using phonenumbers library.
        """
        try:
            parsed_phone = phonenumbers.parse(self.phone_number, "IN")
            if not phonenumbers.is_valid_number(parsed_phone):
                raise ValueError("Invalid phone number")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError("Invalid phone number format")

    def save(self, *args, **kwargs):
        """
        Clean the phone number before saving.
        """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class SpamRecord(models.Model):
    """
    Model to track spam reports for phone numbers.
    """
    phone_number = models.CharField(max_length=15, unique=True)
    spam_count = models.IntegerField(default=0)
    last_reported = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['phone_number']),
        ]

    def clean(self):
        """
        Validate phone number format using phonenumbers library.
        """
        try:
            parsed_phone = phonenumbers.parse(self.phone_number, "IN")
            if not phonenumbers.is_valid_number(parsed_phone):
                raise ValueError("Invalid phone number")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError("Invalid phone number format")

    def save(self, *args, **kwargs):
        """
        Clean the phone number before saving.
        """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.phone_number} marked as spam {self.spam_count} times"


class GlobalPhonebook(models.Model):
    """
    Global phonebook model for managing global contacts and spam status.
    """
    phone_number = models.CharField(max_length=15)
    name = models.CharField(max_length=255)
    is_spam = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['phone_number']),
        ]

    def clean(self):
        """
        Validate phone number format using phonenumbers library.
        """
        try:
            parsed_phone = phonenumbers.parse(self.phone_number, "IN")
            if not phonenumbers.is_valid_number(parsed_phone):
                raise ValueError("Invalid phone number")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError("Invalid phone number format")

    def save(self, *args, **kwargs):
        """
        Clean the phone number before saving.
        """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class SpamReport(models.Model):
    """
    Model for tracking spam reports by users for specific phone numbers.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'phone_number')
        indexes = [
            models.Index(fields=['user', 'phone_number']),
        ]

    def clean(self):
        """
        Validate phone number format using phonenumbers library.
        """
        try:
            parsed_phone = phonenumbers.parse(self.phone_number, "IN")
            if not phonenumbers.is_valid_number(parsed_phone):
                raise ValueError("Invalid phone number")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError("Invalid phone number format")

    def save(self, *args, **kwargs):
        """
        Clean the phone number before saving.
        """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"User {self.user.username} reported {self.phone_number} as spam"
