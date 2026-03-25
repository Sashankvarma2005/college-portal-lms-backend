from rest_framework import generics

from accounts.authentication import JWTAuthentication
from accounts.permissions import RoleBasedMethodPermission
from fees.models import FeePayment, FeeStructure
from fees.serializers import FeePaymentSerializer, FeeStructureSerializer


class FeeStructureListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [RoleBasedMethodPermission]

    required_roles_read = ["STUDENT", "FACULTY", "SuperAdmin", "Admin", "Accountant"]
    required_roles_write = ["SuperAdmin", "Admin", "Accountant"]

    serializer_class = FeeStructureSerializer

    def get_queryset(self):
        return FeeStructure.objects.all().order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save()


class FeeStructureRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [RoleBasedMethodPermission]

    required_roles_read = ["STUDENT", "FACULTY", "SuperAdmin", "Admin", "Accountant"]
    required_roles_write = ["SuperAdmin", "Admin", "Accountant"]

    serializer_class = FeeStructureSerializer
    queryset = FeeStructure.objects.all()


class FeePaymentListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [RoleBasedMethodPermission]

    required_roles_read = ["STUDENT", "SuperAdmin", "Admin", "Accountant"]
    required_roles_write = ["STUDENT", "SuperAdmin", "Admin", "Accountant"]

    serializer_class = FeePaymentSerializer

    def get_queryset(self):
        role = self.request.user.role
        if role == "STUDENT":
            return FeePayment.objects.filter(student_id_id=self.request.user.user_id).order_by(
                "-created_at"
            )
        return FeePayment.objects.all().order_by("-created_at")

    def perform_create(self, serializer):
        role = self.request.user.role
        if role == "STUDENT":
            serializer.save(student_id_id=self.request.user.user_id)
        else:
            serializer.save()

    def perform_update(self, serializer):
        role = self.request.user.role
        payment = serializer.save()
        if role == "STUDENT":
            payment.student_id_id = self.request.user.user_id
            payment.save(update_fields=["student_id"])


class FeePaymentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [RoleBasedMethodPermission]

    required_roles_read = ["STUDENT", "SuperAdmin", "Admin", "Accountant"]
    required_roles_write = ["STUDENT", "SuperAdmin", "Admin", "Accountant"]

    serializer_class = FeePaymentSerializer

    def get_queryset(self):
        role = self.request.user.role
        if role == "STUDENT":
            return FeePayment.objects.filter(student_id_id=self.request.user.user_id)
        return FeePayment.objects.all()

    def perform_update(self, serializer):
        role = self.request.user.role
        payment = serializer.save()
        if role == "STUDENT":
            payment.student_id_id = self.request.user.user_id
            payment.save(update_fields=["student_id"])
