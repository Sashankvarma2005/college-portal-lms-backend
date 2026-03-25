from django.urls import path

from announcements.views import (
    AnnouncementListCreateView,
    AnnouncementRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("", AnnouncementListCreateView.as_view(), name="announcement-list-create"),
    path("<int:pk>/", AnnouncementRetrieveUpdateDestroyView.as_view(), name="announcement-detail"),
]

