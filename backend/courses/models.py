from django.db import models

from accounts.models import FacultyPersonal, Student


class Subject(models.Model):
    class Branch(models.TextChoices):
        CSE = "CSE"
        ECE = "ECE"
        ME = "ME"
        CE = "CE"
        EE = "EE"

    class Meta:
        indexes = [
            models.Index(fields=["branch", "semester"]),
        ]

    id = models.BigAutoField(primary_key=True)
    subject_code = models.CharField(max_length=20, unique=True)
    subject_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=50, choices=Branch.choices)
    semester = models.IntegerField()
    credits = models.IntegerField(default=0)
    theory_marks = models.IntegerField(default=100)
    practical_marks = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.subject_code} - {self.subject_name}"


class Course(models.Model):
    class Section(models.TextChoices):
        A = "A"
        B = "B"
        C = "C"

    id = models.BigAutoField(primary_key=True)
    faculty_id = models.ForeignKey(FacultyPersonal, on_delete=models.CASCADE, related_name="courses")
    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="courses")
    semester = models.IntegerField()
    section = models.CharField(max_length=10, choices=Section.choices)
    academic_year = models.IntegerField()  # e.g., 2024
    total_classes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.subject_id.subject_code} ({self.section})"

