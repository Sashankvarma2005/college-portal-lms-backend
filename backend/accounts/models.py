from django.db import models

class Student(models.Model):
    class Branch(models.TextChoices):
        CSE = "CSE"
        ECE = "ECE"
        ME = "ME"
        CE = "CE"
        EE = "EE"

    id = models.BigAutoField(primary_key=True)
    roll_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=15)
    password_hash = models.CharField(max_length=255)
    branch = models.CharField(max_length=50, choices=Branch.choices)
    semester = models.IntegerField(default=1)
    enrollment_year = models.IntegerField()
    dob = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_roll_number(self) -> None:
        # Generated from branch + enrollment year + primary key for uniqueness.
        # roll_number is initially null/blank to allow creation before PK exists.
        if self.roll_number:
            return
        branch_prefix = (self.branch or "UNK")[:3].upper()
        self.roll_number = f"{branch_prefix}{self.enrollment_year}{self.id:06d}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.roll_number:
            self.set_roll_number()
            super().save(update_fields=["roll_number"])

    def __str__(self) -> str:
        return f"{self.name} ({self.roll_number or 'pending'})"


class FacultyPersonal(models.Model):
    class Designation(models.TextChoices):
        Professor = "Professor"
        AssociateProf = "Associate Prof"
        AssistantProf = "Assistant Prof"

    class Department(models.TextChoices):
        CSE = "CSE"
        ECE = "ECE"
        ME = "ME"
        CE = "CE"
        EE = "EE"

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(max_length=15)
    password_hash = models.CharField(max_length=255)
    designation = models.CharField(max_length=50)
    department = models.CharField(max_length=50, choices=Department.choices)
    qualification = models.CharField(max_length=100, null=True, blank=True)
    experience_years = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.department})"


class Admin(models.Model):
    class Role(models.TextChoices):
        SuperAdmin = "SuperAdmin"
        Admin = "Admin"
        Accountant = "Accountant"

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=Role.choices)
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.role})"


class PasswordResetToken(models.Model):
    class UserType(models.TextChoices):
        STUDENT = "STUDENT"
        FACULTY = "FACULTY"
        ADMIN = "ADMIN"

    id = models.BigAutoField(primary_key=True)
    token = models.CharField(max_length=256, unique=True)
    user_type = models.CharField(max_length=20, choices=UserType.choices)
    email = models.EmailField(max_length=100)
    user_id = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)

    def is_expired(self) -> bool:
        from django.utils import timezone

        return timezone.now() > self.expires_at

    def is_consumed(self) -> bool:
        return self.consumed_at is not None

    def __str__(self) -> str:
        return f"ResetToken({self.user_type}, {self.email})"
