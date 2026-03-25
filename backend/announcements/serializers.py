from rest_framework import serializers

from accounts.models import Admin
from announcements.models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    created_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Announcement
        fields = [
            "id",
            "title",
            "description",
            "created_by",
            "target_audience",
            "expires_at",
            "created_at",
        ]
        read_only_fields = ["created_at"]

