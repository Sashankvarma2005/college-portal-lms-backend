from rest_framework import generics

from accounts.authentication import JWTAuthentication
from accounts.exceptions import ForbiddenException
from accounts.models import FacultyPersonal
from accounts.permissions import RoleBasedMethodPermission
from attendance.models import Attendance
from attendance.serializers import AttendanceSerializer
from courses.models import Course


class AttendanceListCreateView(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [RoleBasedMethodPermission]

    required_roles_read = ["STUDENT", "FACULTY", "SuperAdmin", "Admin", "Accountant"]
    required_roles_write = ["FACULTY", "SuperAdmin", "Admin", "Accountant"]

    serializer_class = AttendanceSerializer

    def get_queryset(self):
        role = self.request.user.role
        if role == "STUDENT":
            return Attendance.objects.filter(student_id_id=self.request.user.user_id).select_related(
                "course_id", "marked_by", "student_id"
            )
        if role == "FACULTY":
            return Attendance.objects.filter(course_id__faculty_id_id=self.request.user.user_id).select_related(
                "course_id", "marked_by", "student_id"
            )
        return Attendance.objects.all().select_related("course_id", "marked_by", "student_id")

    def perform_create(self, serializer):
        role = self.request.user.role
        if role == "FACULTY":
            course_id = serializer.validated_data["course_id"].id
            course = Course.objects.filter(id=course_id, faculty_id_id=self.request.user.user_id).first()
            if not course:
                raise ForbiddenException("You can only mark attendance for your courses.")
            serializer.save(marked_by_id=self.request.user.user_id)
        else:
            # Admin can create attendance for any faculty via 'marked_by'.
            marked_by = serializer.validated_data.get("marked_by")
            if not marked_by:
                raise ForbiddenException("Admin must provide marked_by faculty_id.")
            serializer.save()


class AttendanceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [RoleBasedMethodPermission]
    required_roles_read = ["STUDENT", "FACULTY", "SuperAdmin", "Admin", "Accountant"]
    required_roles_write = ["FACULTY", "SuperAdmin", "Admin", "Accountant"]

    serializer_class = AttendanceSerializer
    queryset = Attendance.objects.all()

    def get_queryset(self):
        role = self.request.user.role
        if role == "STUDENT":
            return Attendance.objects.filter(student_id_id=self.request.user.user_id)
        if role == "FACULTY":
            return Attendance.objects.filter(course_id__faculty_id_id=self.request.user.user_id)
        return Attendance.objects.all()

    def perform_update(self, serializer):
        role = self.request.user.role
        attendance = serializer.save()

        if role == "FACULTY":
            # Ensure updated attendance still belongs to the faculty's course.
            if attendance.course_id.faculty_id_id != self.request.user.user_id:
                raise ForbiddenException("You can only modify attendance for your courses.")
            attendance.marked_by_id = self.request.user.user_id
            attendance.save(update_fields=["marked_by"])

