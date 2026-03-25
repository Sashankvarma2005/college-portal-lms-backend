from django.db import models

from accounts.models import Student
from courses.models import Course, Subject


class Marks(models.Model):
    class Grade(models.TextChoices):
        A_PLUS = "A+"
        A = "A"
        B_PLUS = "B+"
        B = "B"
        C = "C"
        D = "D"
        F = "F"

    id = models.BigAutoField(primary_key=True)
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="marks")
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="marks")
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="marks")
    theory_marks = models.IntegerField(default=0)
    practical_marks = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    grade = models.CharField(max_length=5, choices=Grade.choices, default=Grade.C)
    semester = models.IntegerField()
    academic_year = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["student_id", "subject_id", "course_id", "semester", "academic_year"]

    def __str__(self) -> str:
        return f"Marks(student={self.student_id_id}, subject={self.subject_id_id})"
