from rest_framework import serializers
from .models import User, Contact, GlobalPhonebook,SpamReport,SpamRecord

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number', 'email_address', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'user', 'phone_number', 'name']

class SpamRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpamRecord
        fields = ['phone_number', 'spam_count', 'last_reported']

class GlobalPhonebookSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalPhonebook
        fields = ['phone_number', 'name', 'is_spam']

class SpamReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpamReport
        fields = ['user', 'phone_number', 'reported_at']
        read_only_fields = ['reported_at'] 
