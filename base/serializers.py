from rest_framework import serializers
from .models import User, Contact, SpamReport


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "phone_number", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["name", "phone_number"]

    def create(self, validated_data):
        # Automatically include the authenticated user
        validated_data["owner"] = self.context["request"].user
        return Contact.objects.create(**validated_data)
    
    def validate(self, data):
        request = self.context.get("request")
        phone_number = data.get('phone_number')
        # Check if the contact already exists for the authenticated user.
        if Contact.objects.filter(owner=request.user, phone_number=phone_number).exists():
            raise serializers.ValidationError("A contact with this phone number already exists.")
        return data


class SpamReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpamReport
        fields = ["phone_number"]
        read_only_fields = ["timestamp"]
