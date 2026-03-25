from rest_framework import serializers

from accounts.models import Student
from fees.models import FeePayment, FeeStructure


class FeeStructureSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = FeeStructure
        fields = [
            "id",
            "branch",
            "semester",
            "tuition_fee",
            "hostel_fee",
            "library_fee",
            "lab_fee",
            "total_fee",
            "due_date",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class FeePaymentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), required=False
    )

    class Meta:
        model = FeePayment
        fields = [
            "id",
            "student_id",
            "fee_structure_id",
            "amount_paid",
            "payment_date",
            "transaction_id",
            "payment_status",
            "receipt_number",
            "created_at",
        ]
        read_only_fields = ["created_at"]

