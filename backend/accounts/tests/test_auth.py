import pytest
from rest_framework.test import APIClient
from django.urls import reverse

from accounts.models import Admin, FacultyPersonal, PasswordResetToken, Student
from accounts.utils import hash_password_bcrypt


@pytest.mark.django_db
def test_student_registration_login_profile_rbac():
    client = APIClient()

    # Register Student
    reg_payload = {
        "name": "Rahul Kumar",
        "email": "rahul@test.com",
        "phone": "9876543210",
        "password": "SecurePass@123",
        "branch": "CSE",
        "enrollment_year": 2024,
    }
    resp = client.post("/api/auth/student/register", reg_payload, format="json")
    assert resp.status_code == 201
    assert resp.data["role"] == "STUDENT"
    assert Student.objects.filter(email="rahul@test.com").exists()

    # Login Student -> JWT
    login_payload = {"email": "rahul@test.com", "password": "SecurePass@123"}
    resp = client.post("/api/auth/student/login", login_payload, format="json")
    assert resp.status_code == 200
    assert "token" in resp.data
    assert resp.data["role"] == "STUDENT"

    token = resp.data["token"]
    student = Student.objects.get(email="rahul@test.com")
    assert resp.data["userId"] == student.id

    # Create Faculty directly (since faculty register is open too)
    faculty = FacultyPersonal.objects.create(
        name="Dr. Smith",
        email="smith@test.com",
        phone="9000000000",
        password_hash=hash_password_bcrypt("SecurePass@123"),
        designation="Professor",
        department="CSE",
        qualification="PhD",
        experience_years=3,
    )
    faculty_login = client.post(
        "/api/auth/faculty/login",
        {"email": "smith@test.com", "password": "SecurePass@123"},
        format="json",
    )
    assert faculty_login.status_code == 200
    faculty_token = faculty_login.data["token"]

    # RBAC: Faculty token should be forbidden for student profile
    prof_resp = client.get("/api/student/profile", HTTP_AUTHORIZATION=f"Bearer {faculty_token}")
    assert prof_resp.status_code in (401, 403)

    # RBAC: Student token should succeed
    prof_resp_ok = client.get("/api/student/profile", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert prof_resp_ok.status_code == 200
    assert prof_resp_ok.data["email"] == "rahul@test.com"


@pytest.mark.django_db
def test_password_reset_demo_mode_and_rbac_endpoints():
    client = APIClient()

    # Student exists
    student = Student.objects.create(
        name="Alice",
        email="alice@test.com",
        phone="9000000001",
        password_hash=hash_password_bcrypt("SecurePass@123"),
        branch="CSE",
        enrollment_year=2024,
        semester=1,
    )

    # Forgot password -> should return reset_token (demo mode)
    forgot = client.post("/api/auth/forgot-password", {"email": "alice@test.com"}, format="json")
    assert forgot.status_code == 200
    assert forgot.data["message"] == "Reset link sent to email"
    reset_token = forgot.data["reset_token"]
    assert PasswordResetToken.objects.filter(token=reset_token).exists()

    # Reset password
    new_pass = "NewPass@1234"
    reset = client.post(
        "/api/auth/reset-password",
        {"token": reset_token, "newPassword": new_pass},
        format="json",
    )
    assert reset.status_code == 200

    # Login with new password works
    login = client.post(
        "/api/auth/student/login",
        {"email": "alice@test.com", "password": new_pass},
        format="json",
    )
    assert login.status_code == 200

    # RBAC demo endpoints should be reachable with correct roles
    student_token = login.data["token"]
    enroll_resp = client.get(
        "/api/student/enrollments",
        HTTP_AUTHORIZATION=f"Bearer {student_token}",
    )
    assert enroll_resp.status_code == 200
    assert "enrollments" in enroll_resp.data

    # Faculty role
    faculty = FacultyPersonal.objects.create(
        name="Bob",
        email="bob@test.com",
        phone="9000000002",
        password_hash=hash_password_bcrypt("SecurePass@123"),
        designation="Assistant Prof",
        department="CSE",
        qualification="MSc",
        experience_years=1,
    )
    faculty_login = client.post(
        "/api/auth/faculty/login",
        {"email": "bob@test.com", "password": "SecurePass@123"},
        format="json",
    )
    assert faculty_login.status_code == 200
    faculty_token = faculty_login.data["token"]
    faculty_students_resp = client.get(
        "/api/faculty/students",
        HTTP_AUTHORIZATION=f"Bearer {faculty_token}",
    )
    assert faculty_students_resp.status_code == 200
    assert "students" in faculty_students_resp.data

    # Admin role endpoint
    admin = Admin.objects.create(
        name="Admin1",
        email="admin@test.com",
        password_hash=hash_password_bcrypt("SecurePass@123"),
        role="SuperAdmin",
        phone="9000000003",
    )
    admin_login = client.post(
        "/api/auth/admin/login",
        {"email": "admin@test.com", "password": "SecurePass@123"},
        format="json",
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.data["token"]
    admin_reports_resp = client.get(
        "/api/admin/reports",
        HTTP_AUTHORIZATION=f"Bearer {admin_token}",
    )
    assert admin_reports_resp.status_code == 200
    assert "reports" in admin_reports_resp.data

