from rest_framework import serializers

from accounts.models import FacultyPersonal, Student
from attendance.models import Attendance
from courses.models import Course


class AttendanceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    marked_by = serializers.PrimaryKeyRelatedField(
        queryset=FacultyPersonal.objects.all(), required=False
    )

    class Meta:
        model = Attendance
        fields = [
            "id",
            "student_id",
            "course_id",
            "class_date",
            "status",
            "marked_by",
            "created_at",
        ]
        read_only_fields = ["created_at"]

