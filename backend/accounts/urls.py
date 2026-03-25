from django.urls import path

from .views import (
    AdminLoginView,
    AdminRegisterView,
    ChangePasswordView,
    AdminReportsView,
    FacultyLoginView,
    FacultyRegisterView,
    ForgotPasswordView,
    ResetPasswordView,
    FacultyStudentsView,
    StudentLoginView,
    StudentEnrollmentsView,
    StudentProfileView,
    StudentRegisterView,
)

urlpatterns = [
    # Registration
    path("auth/student/register", StudentRegisterView.as_view(), name="student-register"),
    path("auth/faculty/register", FacultyRegisterView.as_view(), name="faculty-register"),
    path("auth/admin/register", AdminRegisterView.as_view(), name="admin-register"),

    # Login
    path("auth/student/login", StudentLoginView.as_view(), name="student-login"),
    path("auth/faculty/login", FacultyLoginView.as_view(), name="faculty-login"),
    path("auth/admin/login", AdminLoginView.as_view(), name="admin-login"),

    # Password reset
    path("auth/forgot-password", ForgotPasswordView.as_view(), name="forgot-password"),
    path("auth/reset-password", ResetPasswordView.as_view(), name="reset-password"),

    # Profile
    path("student/profile", StudentProfileView.as_view(), name="student-profile"),

    # Week 5 protected demo endpoints (RBAC)
    path("student/enrollments", StudentEnrollmentsView.as_view(), name="student-enrollments"),
    path("faculty/students", FacultyStudentsView.as_view(), name="faculty-students"),
    path("admin/reports", AdminReportsView.as_view(), name="admin-reports"),

    # Change password
    path("auth/change-password", ChangePasswordView.as_view(), name="change-password"),
]

