from django.db import models

from accounts.models import Student
from courses.models import Course, Subject


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE"
        DROPPED = "DROPPED"
        COMPLETED = "COMPLETED"

    id = models.BigAutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="enrollments")
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    semester = models.IntegerField()
    academic_year = models.IntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    enrolled_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["student_id", "course_id", "academic_year", "semester"]

    def __str__(self) -> str:
        return f"Enrollment(student={self.student_id_id}, course={self.course_id_id}, {self.academic_year})"
