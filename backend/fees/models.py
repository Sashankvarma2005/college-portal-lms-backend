from django.db import models

from accounts.models import Student


class FeeStructure(models.Model):
    class Meta:
        indexes = [models.Index(fields=["branch", "semester"])]

    id = models.BigAutoField(primary_key=True)
    branch = models.CharField(max_length=50)
    semester = models.IntegerField()
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2)
    hostel_fee = models.DecimalField(max_digits=10, decimal_places=2)
    library_fee = models.DecimalField(max_digits=10, decimal_places=2)
    lab_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"FeeStructure({self.branch}, sem={self.semester})"


class FeePayment(models.Model):
    class Meta:
        indexes = [models.Index(fields=["payment_status"])]

    class PaymentStatus(models.TextChoices):
        PENDING = "PENDING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"

    id = models.BigAutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fee_payments")
    fee_structure_id = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name="payments")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField()
    transaction_id = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    receipt_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"FeePayment({self.student_id_id}, receipt={self.receipt_number})"

