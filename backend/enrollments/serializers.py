from rest_framework import serializers

from accounts.models import Student
from courses.models import Course, Subject
from enrollments.models import Enrollment


class EnrollmentBaseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    # Enrollment.student_id is a FK object; expose the integer id instead.
    student_id = serializers.IntegerField(source="student_id_id", read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    course_id = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Enrollment
        fields = [
            "id",
            "student_id",
            "subject_id",
            "course_id",
            "semester",
            "academic_year",
            "status",
            "enrolled_date",
        ]
        read_only_fields = ["enrolled_date"]


class EnrollmentStudentSerializer(EnrollmentBaseSerializer):
    """
    STUDENT create/update: student_id comes from JWT, not request body.
    """


class EnrollmentAdminSerializer(EnrollmentBaseSerializer):
    """
    ADMIN create/update: allow selecting student_id.
    """

    student_id = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

