from django.urls import path

from enrollments.views import (
    EnrollmentListCreateView,
    EnrollmentRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("", EnrollmentListCreateView.as_view(), name="enrollment-list-create"),
    path("<int:pk>/", EnrollmentRetrieveUpdateDestroyView.as_view(), name="enrollment-detail"),
]

