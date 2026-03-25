from rest_framework import serializers

from .exceptions import UserAlreadyExistsException
from .models import Admin, FacultyPersonal, Student
from .utils import validate_password_strength, hash_password_bcrypt


class StudentRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=100)
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)
    branch = serializers.ChoiceField(choices=Student.Branch.choices)
    enrollment_year = serializers.IntegerField(min_value=1900, max_value=3000)

    def validate_email(self, value):
        if Student.objects.filter(email=value).exists():
            raise UserAlreadyExistsException()
        return value

    def validate_password(self, value):
        validate_password_strength(value)
        return value

    def create(self, validated_data) -> Student:
        password = validated_data.pop("password")
        student = Student.objects.create(
            name=validated_data["name"],
            email=validated_data["email"],
            phone=validated_data["phone"],
            password_hash=hash_password_bcrypt(password),
            branch=validated_data["branch"],
            enrollment_year=validated_data["enrollment_year"],
        )
        return student


class FacultyRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=100)
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)
    department = serializers.ChoiceField(choices=FacultyPersonal.Department.choices)
    designation = serializers.CharField()
    qualification = serializers.CharField(required=False, allow_blank=True)
    experience_years = serializers.IntegerField(required=False, default=0)

    def validate_designation(self, value):
        # Accept exact labels from schema
        allowed = {c for c, _ in FacultyPersonal.Designation.choices}
        if value not in allowed:
            # Also accept "Associate Prof" -> stored as "Associate Prof"
            raise serializers.ValidationError(f"Invalid designation. Allowed: {sorted(allowed)}")
        return value

    def validate_email(self, value):
        if FacultyPersonal.objects.filter(email=value).exists():
            raise UserAlreadyExistsException()
        return value

    def validate_password(self, value):
        validate_password_strength(value)
        return value

    def create(self, validated_data) -> FacultyPersonal:
        password = validated_data.pop("password")
        faculty = FacultyPersonal.objects.create(
            name=validated_data["name"],
            email=validated_data["email"],
            phone=validated_data["phone"],
            password_hash=hash_password_bcrypt(password),
            department=validated_data["department"],
            designation=validated_data["designation"],
            qualification=validated_data.get("qualification") or None,
            experience_years=validated_data.get("experience_years", 0),
        )
        return faculty


class AdminRegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField(max_length=100)
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=Admin.Role.choices)

    def validate_email(self, value):
        if Admin.objects.filter(email=value).exists():
            raise UserAlreadyExistsException()
        return value

    def validate_password(self, value):
        validate_password_strength(value)
        return value

    def create(self, validated_data) -> Admin:
        password = validated_data.pop("password")
        admin = Admin.objects.create(
            name=validated_data["name"],
            email=validated_data["email"],
            phone=validated_data["phone"],
            password_hash=hash_password_bcrypt(password),
            role=validated_data["role"],
        )
        return admin


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=256)
    newPassword = serializers.CharField(write_only=True)

    def validate_newPassword(self, value):
        validate_password_strength(value)
        return value


class StudentProfileUpdateSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15, required=False)
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    pincode = serializers.CharField(required=False, allow_blank=True)
    dob = serializers.DateField(required=False)


class ChangePasswordSerializer(serializers.Serializer):
    oldPassword = serializers.CharField(write_only=True)
    newPassword = serializers.CharField(write_only=True)

    def validate_newPassword(self, value):
        validate_password_strength(value)
        return value

