from django.db import models

from accounts.models import Admin


class Announcement(models.Model):
    class TargetAudience(models.TextChoices):
        STUDENT = "STUDENT"
        FACULTY = "FACULTY"
        ALL = "ALL"

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name="announcements")
    target_audience = models.CharField(max_length=50, choices=TargetAudience.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateField()

    def __str__(self) -> str:
        return f"{self.title} ({self.target_audience})"
