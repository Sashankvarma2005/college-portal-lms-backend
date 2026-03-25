from django.db import models

from accounts.models import FacultyPersonal, Student
from courses.models import Course


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "PRESENT"
        ABSENT = "ABSENT"
        LEAVE = "LEAVE"

    id = models.BigAutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance")
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="attendance")
    class_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices)
    marked_by = models.ForeignKey(
        FacultyPersonal, on_delete=models.CASCADE, related_name="attendance_marked"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["student_id", "course_id", "class_date"]

    def __str__(self) -> str:
        return f"Attendance({self.student_id_id}, {self.course_id_id}, {self.class_date})"
