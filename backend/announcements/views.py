from django.utils import timezone
from rest_framework import generics

from accounts.authentication import JWTAuthentication
from accounts.permissions import RoleBasedMethodPermission
from announcements.models import Announcement
from announcements.serializers import AnnouncementSerializer


class AnnouncementListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [RoleBasedMethodPermission]

    required_roles_read = ["STUDENT", "FACULTY", "SuperAdmin", "Admin", "Accountant"]
    required_roles_write = ["SuperAdmin", "Admin", "Accountant"]

    serializer_class = AnnouncementSerializer

    def get_queryset(self):
        today = timezone.now().date()
        base = Announcement.objects.filter(expires_at__gte=today).order_by("-created_at")
        role = self.request.user.role
        if role == "STUDENT":
            return base.filter(target_audience__in=["STUDENT", "ALL"])
        if role == "FACULTY":
            return base.filter(target_audience__in=["FACULTY", "ALL"])
        return base

    def perform_create(self, serializer):
        serializer.save(created_by_id=self.request.user.user_id)


class AnnouncementRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [RoleBasedMethodPermission]

    required_roles_read = ["STUDENT", "FACULTY", "SuperAdmin", "Admin", "Accountant"]
    required_roles_write = ["SuperAdmin", "Admin", "Accountant"]

    serializer_class = AnnouncementSerializer

    def get_queryset(self):
        today = timezone.now().date()
        base = Announcement.objects.filter(expires_at__gte=today)
        role = self.request.user.role
        if role == "STUDENT":
            return base.filter(target_audience__in=["STUDENT", "ALL"])
        if role == "FACULTY":
            return base.filter(target_audience__in=["FACULTY", "ALL"])
        return base

    def perform_update(self, serializer):
        serializer.save()
