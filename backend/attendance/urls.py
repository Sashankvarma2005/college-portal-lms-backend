from django.urls import path

from attendance.views import (
    AttendanceListCreateView,
    AttendanceRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("", AttendanceListCreateView.as_view(), name="attendance-list-create"),
    path("<int:pk>/", AttendanceRetrieveUpdateDestroyView.as_view(), name="attendance-detail"),
]

