import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Admin, FacultyPersonal, Student
from accounts.utils import hash_password_bcrypt
from announcements.models import Announcement
from attendance.models import Attendance
from courses.models import Course, Subject
from enrollments.models import Enrollment
from fees.models import FeePayment, FeeStructure


@pytest.mark.django_db
def test_crud_enrollments_attendance_fees_announcements():
    client = APIClient()

    faculty = FacultyPersonal.objects.create(
        name="Dr. X",
        email="fac@test.com",
        phone="9000000000",
        password_hash=hash_password_bcrypt("SecurePass@123"),
        designation="Professor",
        department="CSE",
        qualification="PhD",
        experience_years=5,
    )

    student = Student.objects.create(
        name="Stu Y",
        email="stu@test.com",
        phone="9000000001",
        password_hash=hash_password_bcrypt("SecurePass@123"),
        branch="CSE",
        semester=1,
        enrollment_year=2024,
    )

    admin = Admin.objects.create(
        name="Admin Z",
        email="admin@test.com",
        password_hash=hash_password_bcrypt("SecurePass@123"),
        role="SuperAdmin",
        phone="9000000002",
    )

    subject = Subject.objects.create(
        subject_code="CS101",
        subject_name="Intro to CS",
        branch="CSE",
        semester=1,
        credits=4,
        theory_marks=100,
        practical_marks=50,
    )
    course = Course.objects.create(
        faculty_id=faculty,
        subject_id=subject,
        semester=1,
        section="A",
        academic_year=2024,
        total_classes=30,
    )

    # Login tokens
    student_token = client.post(
        "/api/auth/student/login",
        {"email": student.email, "password": "SecurePass@123"},
        format="json",
    ).data["token"]
    faculty_token = client.post(
        "/api/auth/faculty/login",
        {"email": faculty.email, "password": "SecurePass@123"},
        format="json",
    ).data["token"]
    admin_token = client.post(
        "/api/auth/admin/login",
        {"email": admin.email, "password": "SecurePass@123"},
        format="json",
    ).data["token"]

    # Enrollments CRUD (student)
    create_enroll = client.post(
        "/api/enrollments/",
        {
            "subject_id": subject.id,
            "course_id": course.id,
            "semester": 1,
            "academic_year": 2024,
            "status": "ACTIVE",
        },
        HTTP_AUTHORIZATION=f"Bearer {student_token}",
        format="json",
    )
    assert create_enroll.status_code == 201, create_enroll.data
    enroll_id = create_enroll.data["id"]

    list_enroll = client.get(
        "/api/enrollments/",
        HTTP_AUTHORIZATION=f"Bearer {student_token}",
    )
    assert list_enroll.status_code == 200
    assert len(list_enroll.data) >= 1

    update_enroll = client.put(
        f"/api/enrollments/{enroll_id}/",
        {
            "status": "DROPPED",
            "subject_id": subject.id,
            "course_id": course.id,
            "semester": 1,
            "academic_year": 2024,
        },
        HTTP_AUTHORIZATION=f"Bearer {student_token}",
        format="json",
    )
    assert update_enroll.status_code == 200

    delete_enroll = client.delete(
        f"/api/enrollments/{enroll_id}/",
        HTTP_AUTHORIZATION=f"Bearer {student_token}",
    )
    assert delete_enroll.status_code in (204, 200)
    assert not Enrollment.objects.filter(id=enroll_id).exists()

    # Attendance CRUD
    # Student should be forbidden to create attendance (write-only for faculty/admin)
    forbidden_att = client.post(
        "/api/attendance/",
        {
            "student_id": student.id,
            "course_id": course.id,
            "class_date": str(timezone.now().date()),
            "status": "PRESENT",
        },
        HTTP_AUTHORIZATION=f"Bearer {student_token}",
        format="json",
    )
    assert forbidden_att.status_code == 403

    mark_att = client.post(
        "/api/attendance/",
        {
            "student_id": student.id,
            "course_id": course.id,
            "class_date": str(timezone.now().date()),
            "status": "PRESENT",
        },
        HTTP_AUTHORIZATION=f"Bearer {faculty_token}",
        format="json",
    )
    assert mark_att.status_code == 201
    att_id = mark_att.data["id"]

    student_att_list = client.get(
        "/api/attendance/",
        HTTP_AUTHORIZATION=f"Bearer {student_token}",
    )
    assert student_att_list.status_code == 200
    assert len(student_att_list.data) >= 1

    update_att = client.put(
        f"/api/attendance/{att_id}/",
        {
            "student_id": student.id,
            "course_id": course.id,
            "class_date": str(timezone.now().date()),
            "status": "ABSENT",
        },
        HTTP_AUTHORIZATION=f"Bearer {faculty_token}",
        format="json",
    )
    assert update_att.status_code == 200

    # Fees CRUD
    create_structure = client.post(
        "/api/fees/structures/",
        {
            "branch": "CSE",
            "semester": 1,
            "tuition_fee": "10000.00",
            "hostel_fee": "2000.00",
            "library_fee": "500.00",
            "lab_fee": "1500.00",
            "total_fee": "14000.00",
            "due_date": str((timezone.now().date())),
        },
        HTTP_AUTHORIZATION=f"Bearer {admin_token}",
        format="json",
    )
    assert create_structure.status_code == 201
    structure_id = create_structure.data["id"]

    create_payment = client.post(
        "/api/fees/payments/",
        {
            "fee_structure_id": structure_id,
            "amount_paid": "14000.00",
            "payment_date": timezone.now().isoformat(),
            "transaction_id": "TXN1",
            "payment_status": "COMPLETED",
            "receipt_number": "RCPT-1",
        },
        HTTP_AUTHORIZATION=f"Bearer {student_token}",
        format="json",
    )
    assert create_payment.status_code == 201
    payment_id = create_payment.data["id"]

    student_payments = client.get(
        "/api/fees/payments/",
        HTTP_AUTHORIZATION=f"Bearer {student_token}",
    )
    assert student_payments.status_code == 200
    assert len(student_payments.data) >= 1

    update_payment = client.put(
        f"/api/fees/payments/{payment_id}/",
        {
            "fee_structure_id": structure_id,
            "amount_paid": "14000.00",
            "payment_date": timezone.now().isoformat(),
            "transaction_id": "TXN1",
            "payment_status": "COMPLETED",
            "receipt_number": "RCPT-1",
            "student_id": student.id,
        },
        HTTP_AUTHORIZATION=f"Bearer {student_token}",
        format="json",
    )
    assert update_payment.status_code == 200

    delete_payment = client.delete(
        f"/api/fees/payments/{payment_id}/",
        HTTP_AUTHORIZATION=f"Bearer {admin_token}",
    )
    assert delete_payment.status_code in (204, 200)

    # Announcements CRUD
    future_date = timezone.now().date() + timezone.timedelta(days=7)
    past_date = timezone.now().date() - timezone.timedelta(days=2)

    create_announce = client.post(
        "/api/announcements/",
        {
            "title": "Test Announcement",
            "description": "Hello",
            "target_audience": "STUDENT",
            "expires_at": str(future_date),
        },
        HTTP_AUTHORIZATION=f"Bearer {admin_token}",
        format="json",
    )
    assert create_announce.status_code == 201
    announce_id = create_announce.data["id"]

    create_expired = client.post(
        "/api/announcements/",
        {
            "title": "Expired",
            "description": "Old",
            "target_audience": "STUDENT",
            "expires_at": str(past_date),
        },
        HTTP_AUTHORIZATION=f"Bearer {admin_token}",
        format="json",
    )
    assert create_expired.status_code == 201

    student_ann = client.get(
        "/api/announcements/",
        HTTP_AUTHORIZATION=f"Bearer {student_token}",
    )
    assert student_ann.status_code == 200
    titles = [a["title"] for a in student_ann.data]
    assert "Test Announcement" in titles
    assert "Expired" not in titles

    update_announce = client.put(
        f"/api/announcements/{announce_id}/",
        {
            "title": "Updated Title",
            "description": "Hello",
            "target_audience": "STUDENT",
            "expires_at": str(future_date),
        },
        HTTP_AUTHORIZATION=f"Bearer {admin_token}",
        format="json",
    )
    assert update_announce.status_code == 200

    delete_announce = client.delete(
        f"/api/announcements/{announce_id}/",
        HTTP_AUTHORIZATION=f"Bearer {admin_token}",
    )
    assert delete_announce.status_code in (204, 200)
    assert not Announcement.objects.filter(id=announce_id).exists()

