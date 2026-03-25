from rest_framework import generics

from accounts.authentication import JWTAuthentication
from accounts.permissions import RoleBasedPermission
from enrollments.models import Enrollment
from enrollments.serializers import (
    EnrollmentAdminSerializer,
    EnrollmentStudentSerializer,
)


class EnrollmentListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [RoleBasedPermission]
    required_roles = ["STUDENT", "SuperAdmin", "Admin", "Accountant"]

    student_serializer_class = EnrollmentStudentSerializer
    admin_serializer_class = EnrollmentAdminSerializer

    def get_serializer_class(self):
        if self.request.user.role == "STUDENT":
            return self.student_serializer_class
        return self.admin_serializer_class

    def get_queryset(self):
        role = self.request.user.role
        if role == "STUDENT":
            return Enrollment.objects.filter(student_id_id=self.request.user.user_id)
        return Enrollment.objects.all()

    def perform_create(self, serializer):
        role = self.request.user.role
        if role == "STUDENT":
            serializer.save(student_id_id=self.request.user.user_id)
        else:
            serializer.save()


class EnrollmentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [RoleBasedPermission]
    required_roles = ["STUDENT", "SuperAdmin", "Admin", "Accountant"]

    student_serializer_class = EnrollmentStudentSerializer
    admin_serializer_class = EnrollmentAdminSerializer

    def get_serializer_class(self):
        if self.request.user.role == "STUDENT":
            return self.student_serializer_class
        return self.admin_serializer_class

    def get_queryset(self):
        role = self.request.user.role
        if role == "STUDENT":
            return Enrollment.objects.filter(student_id_id=self.request.user.user_id)
        return Enrollment.objects.all()

    def perform_update(self, serializer):
        role = self.request.user.role
        enrollment = serializer.save()
        if role == "STUDENT":
            enrollment.student_id_id = self.request.user.user_id
            enrollment.save(update_fields=["student_id"])
