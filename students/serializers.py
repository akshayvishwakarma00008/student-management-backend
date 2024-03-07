from rest_framework import serializers
from .models import Student, FeePayment, StudentEnrollmentHistory
from django.utils import timezone
import uuid


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            "fullname",
            "age",
            "registrationNo",
            "email",
            "course",
            "phoneNumber",
            "address",
            "total_fees_paid",
            "pen_fees",
            "class_enrolled",
            "academic_year",
        ]


class FeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePayment
        fields = ["payment_date", "amount", "payment_type", "student"]

    def validate(self, attrs):
        date = attrs.get("payment_date")
        today = timezone.now().date()

        if date > today:
            raise serializers.ValidationError(
                "Payment date cannot be greater than today"
            )
        return attrs


class StudentEnrollmentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEnrollmentHistory
        fields = [
            "academic_year",
            "total_fees_paid",
            "pen_fees",
            "class_enrolled",
            "student",
        ]
