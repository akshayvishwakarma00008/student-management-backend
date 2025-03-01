from rest_framework import serializers
from .models import Student, FeePayment, StudentEnrollmentHistory
from django.utils import timezone
import uuid


class StudentSerializer(serializers.ModelSerializer):
    total_fees = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = "__all__"

    def get_total_fees(self, obj):
        """Fetch total_fees from related class_enrolled"""
        if obj.class_enrolled:
            return obj.class_enrolled.total_fees
        return 0


class FeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePayment
        fields = "__all__"

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
