from datetime import timedelta
from typing import Any

from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import JWTAuthentication
from .jwt_utils import generate_jwt
from .exceptions import InvalidCredentialsException
from .models import Admin, FacultyPersonal, PasswordResetToken, Student
from .permissions import RoleBasedPermission
from .serializers import (
    AdminRegisterSerializer,
    ChangePasswordSerializer,
    FacultyRegisterSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    ResetPasswordSerializer,
    StudentProfileUpdateSerializer,
    StudentRegisterSerializer,
)
from .utils import check_password_bcrypt, generate_reset_token, hash_password_bcrypt

from courses.models import Course
from enrollments.models import Enrollment


class StudentRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = StudentRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()

        return Response(
            {
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "role": "STUDENT",
                "message": "Registration successful. Please login.",
            },
            status=status.HTTP_201_CREATED,
        )


class FacultyRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FacultyRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        faculty = serializer.save()

        return Response(
            {
                "id": faculty.id,
                "name": faculty.name,
                "email": faculty.email,
                "role": "FACULTY",
                "message": "Registration successful. Please login.",
            },
            status=status.HTTP_201_CREATED,
        )


class AdminRegisterView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [RoleBasedPermission]
    required_roles = ["SuperAdmin"]

    def post(self, request):
        serializer = AdminRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin = serializer.save()

        return Response(
            {
                "id": admin.id,
                "name": admin.name,
                "email": admin.email,
                "role": admin.role,
                "message": "Registration successful.",
            },
            status=status.HTTP_201_CREATED,
        )


def _login_response(*, user_id: int, email: str, name: str, role: str) -> dict[str, Any]:
    token = generate_jwt(user_id=user_id, email=email, role=role)
    return {
        "token": token,
        "type": "Bearer",
        "userId": user_id,
        "email": email,
        "name": name,
        "role": role,
    }


class StudentLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            student = Student.objects.get(email=email)
        except Student.DoesNotExist:
            raise InvalidCredentialsException()

        if not check_password_bcrypt(password, student.password_hash):
            raise InvalidCredentialsException()

        return Response(_login_response(user_id=student.id, email=student.email, name=student.name, role="STUDENT"))


class FacultyLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            faculty = FacultyPersonal.objects.get(email=email)
        except FacultyPersonal.DoesNotExist:
            raise InvalidCredentialsException()

        if not check_password_bcrypt(password, faculty.password_hash):
            raise InvalidCredentialsException()

        return Response(
            _login_response(user_id=faculty.id, email=faculty.email, name=faculty.name, role="FACULTY")
        )


class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            admin = Admin.objects.get(email=email)
        except Admin.DoesNotExist:
            raise InvalidCredentialsException()

        if not check_password_bcrypt(password, admin.password_hash):
            raise InvalidCredentialsException()

        return Response(
            _login_response(user_id=admin.id, email=admin.email, name=admin.name, role=admin.role)
        )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        reset_token = generate_reset_token()
        expires_at = timezone.now() + timedelta(days=1)

        # Demo-mode: we create a record for the matching user type (if any),
        # and return token in response so you can test reset in Postman.
        user_type = None
        user_id = None

        student = Student.objects.filter(email=email).first()
        if student:
            user_type = PasswordResetToken.UserType.STUDENT
            user_id = student.id
        else:
            faculty = FacultyPersonal.objects.filter(email=email).first()
            if faculty:
                user_type = PasswordResetToken.UserType.FACULTY
                user_id = faculty.id
            else:
                admin = Admin.objects.filter(email=email).first()
                if admin:
                    user_type = PasswordResetToken.UserType.ADMIN
                    user_id = admin.id

        # Always respond the same message for security.
        if user_id and user_type:
            PasswordResetToken.objects.create(
                token=reset_token,
                user_type=user_type,
                email=email,
                user_id=user_id,
                expires_at=expires_at,
            )

            # In a real setup we'd send email here.
            # For this assignment demo, we return the reset token.
            return Response(
                {"message": "Reset link sent to email", "reset_token": reset_token},
                status=status.HTTP_200_OK,
            )

        return Response({"message": "Reset link sent to email"}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["newPassword"]

        reset = PasswordResetToken.objects.filter(token=token).first()
        if not reset or reset.is_consumed() or reset.is_expired():
            return Response({"message": "Invalid or expired reset token."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the matching user type.
        new_hash = hash_password_bcrypt(new_password)
        if reset.user_type == PasswordResetToken.UserType.STUDENT:
            obj = Student.objects.filter(id=reset.user_id).first()
        elif reset.user_type == PasswordResetToken.UserType.FACULTY:
            obj = FacultyPersonal.objects.filter(id=reset.user_id).first()
        else:
            obj = Admin.objects.filter(id=reset.user_id).first()

        if not obj:
            return Response({"message": "Reset token user not found."}, status=status.HTTP_400_BAD_REQUEST)

        obj.password_hash = new_hash
        obj.save(update_fields=["password_hash"])

        reset.consumed_at = timezone.now()
        reset.save(update_fields=["consumed_at"])

        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)


class StudentProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [RoleBasedPermission]
    required_roles = ["STUDENT"]

    def get(self, request):
        student = Student.objects.filter(id=request.user.user_id).first()
        if not student:
            return Response({"message": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "name": student.name,
                "email": student.email,
                "roll_no": student.roll_number,
                "branch": student.branch,
                "semester": student.semester,
                "enrollment_year": student.enrollment_year,
                "phone": student.phone,
                "address": student.address,
                "city": student.city,
                "pincode": student.pincode,
            }
        )

    def put(self, request):
        student = Student.objects.filter(id=request.user.user_id).first()
        if not student:
            return Response({"message": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentProfileUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        allowed_fields = {"phone", "address", "city", "pincode", "dob"}
        for field, value in data.items():
            if field in allowed_fields:
                setattr(student, field, value)
        student.save()

        return Response({"message": "Profile updated successfully."})


class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [RoleBasedPermission]
    # required_roles intentionally omitted to allow STUDENT/FACULTY/ADMIN.

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data["oldPassword"]
        new_password = serializer.validated_data["newPassword"]
        new_hash = hash_password_bcrypt(new_password)

        role = request.user.role

        if role == "STUDENT":
            user = Student.objects.filter(id=request.user.user_id).first()
        elif role == "FACULTY":
            user = FacultyPersonal.objects.filter(id=request.user.user_id).first()
        else:
            user = Admin.objects.filter(id=request.user.user_id).first()

        if not user:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if not check_password_bcrypt(old_password, user.password_hash):
            return Response({"message": "Old password is incorrect."}, status=status.HTTP_401_UNAUTHORIZED)

        user.password_hash = new_hash
        user.save(update_fields=["password_hash"])
        return Response({"message": "Password changed successfully."})


class StudentEnrollmentsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [RoleBasedPermission]
    required_roles = ["STUDENT"]

    def get(self, request):
        enrollments = (
            Enrollment.objects.filter(student_id_id=request.user.user_id)
            .select_related("course_id", "course_id__subject_id", "course_id__faculty_id", "subject_id")
            .order_by("-enrolled_date")
        )

        data = []
        for e in enrollments:
            data.append(
                {
                    "id": e.id,
                    "course_id": e.course_id_id,
                    "subject_id": e.subject_id_id,
                    "semester": e.semester,
                    "academic_year": e.academic_year,
                    "status": e.status,
                    "subject_code": e.subject_id.subject_code,
                    "subject_name": e.subject_id.subject_name,
                }
            )

        return Response({"enrollments": data})


class FacultyStudentsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [RoleBasedPermission]
    required_roles = ["FACULTY"]

    def get(self, request):
        faculty_id = request.user.user_id
        course_ids = Course.objects.filter(faculty_id_id=faculty_id).values_list("id", flat=True)

        enrollments = (
            Enrollment.objects.filter(course_id_id__in=course_ids)
            .select_related("student_id")
            .order_by("student_id__roll_number")
        )

        unique_students = {}
        for e in enrollments:
            s = e.student_id
            unique_students[s.id] = {
                "id": s.id,
                "roll_no": s.roll_number,
                "name": s.name,
                "email": s.email,
                "branch": s.branch,
                "semester": s.semester,
            }

        return Response({"students": list(unique_students.values())})


class AdminReportsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [RoleBasedPermission]
    required_roles = ["SuperAdmin", "Admin", "Accountant"]

    def get(self, request):
        # Minimal "reports" summary for demo/testing.
        from announcements.models import Announcement
        from attendance.models import Attendance
        from courses.models import Course, Subject
        from enrollments.models import Enrollment
        from fees.models import FeePayment, FeeStructure
        from marks.models import Marks

        summary = {
            "students_count": Student.objects.count(),
            "faculty_count": FacultyPersonal.objects.count(),
            "admins_count": Admin.objects.count(),
            "subjects_count": Subject.objects.count(),
            "courses_count": Course.objects.count(),
            "enrollments_count": Enrollment.objects.count(),
            "attendance_count": Attendance.objects.count(),
            "marks_count": Marks.objects.count(),
            "fee_structures_count": FeeStructure.objects.count(),
            "fee_payments_count": FeePayment.objects.count(),
            "announcements_count": Announcement.objects.count(),
        }

        return Response({"reports": summary})
