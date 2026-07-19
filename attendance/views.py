from datetime import date

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models.deletion import ProtectedError, RestrictedError

from elementary_back.permissions import (
    IsAdminOrTeacher,
    IsAdminRole,
    can_access_student_classrooms,
    classroom_id_for_attendance,
    is_admin_user,
    require_admin,
    require_classroom_access,
    require_student_classroom_access,
)
from attendance.application.dto.attendance_dto import (
    CreateAttendanceCommand,
    UpdateAttendanceCommand,
)
from attendance.domain.exceptions.attendance_exceptions import (
    AttendanceAlreadyExistsError,
    AttendanceNotFoundError,
    ClassRoomNotFoundError,
    StateCodeNotFoundError,
    StudentNotFoundForAttendanceError,
)
from attendance.interfaces.http.attendance_use_case_factory import (
    build_create_attendance_use_case,
    build_list_attendance_use_case,
    build_update_attendance_use_case,
)
from attendance.models import CatalogTypeAtendance
from .serializer import AttendanceCatalogSerializer
# Create your views here.


class AttendaceView(APIView):
    permission_classes = [IsAdminOrTeacher]

    def get(self, request,class_id=None,date=None,student_id=None):
        if class_id:
            require_classroom_access(request.user, class_id)
        elif student_id:
            from attendance.models import Attendance

            classroom_ids = Attendance.objects.filter(
                student_id=student_id,
                date=date,
            ).values_list("class_room_id", flat=True)
            if classroom_ids:
                for classroom_id in classroom_ids:
                    require_classroom_access(request.user, classroom_id)
            elif not can_access_student_classrooms(request.user, student_id):
                require_admin(request.user)
        else:
            require_admin(request.user)

        use_case = build_list_attendance_use_case()
        attendance_data = use_case.execute(
            class_id=str(class_id) if class_id else None,
            attendance_date=date,
            student_id=str(student_id) if student_id else None,
        )
        return Response(attendance_data)

    def post(self, request, class_id=None):
        if not class_id:
            require_admin(request.user)
            return Response({"error": "Class ID is required"}, status=400)

        require_classroom_access(request.user, class_id)

        student_id = request.data.get("student")
        state_code_id = request.data.get("state_code")
        attendance_date = request.data.get("date")

        if not student_id or not state_code_id or not attendance_date:
            return Response(
                {"error": "student, state_code and date are required"},
                status=400,
            )

        require_student_classroom_access(request.user, student_id, class_id)

        use_case = build_create_attendance_use_case()
        try:
            command = CreateAttendanceCommand(
                student_id=str(student_id),
                state_code_id=str(state_code_id),
                class_id=str(class_id),
                attendance_date=date.fromisoformat(attendance_date),
            )
            data = use_case.execute(command)
            return Response(data, status=201)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        except AttendanceAlreadyExistsError as exc:
            return Response({"error": str(exc)}, status=400)
        except StudentNotFoundForAttendanceError as exc:
            return Response({"error": str(exc)}, status=400)
        except StateCodeNotFoundError as exc:
            return Response({"error": str(exc)}, status=400)
        except ClassRoomNotFoundError as exc:
            return Response({"error": str(exc)}, status=400)

    def patch(self, request, id=None):
        if not id:
            return Response({"error": "Attendance ID is required"}, status=400)

        classroom_id = classroom_id_for_attendance(id)
        if classroom_id is None:
            if not is_admin_user(request.user):
                require_admin(request.user)
        else:
            require_classroom_access(request.user, classroom_id)

        update_use_case = build_update_attendance_use_case()
        try:
            command = UpdateAttendanceCommand(
                attendance_id=str(id),
                state_code_id=str(request.data.get("state_code")) if request.data.get("state_code") else None,
            )
            data = update_use_case.execute(command)
            return Response(data, status=200)
        except AttendanceNotFoundError as exc:
            return Response({"error": str(exc)}, status=404)
        except StateCodeNotFoundError as exc:
            return Response({"error": str(exc)}, status=400)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)

class AttendanceCatalogView(APIView):
    def get_permissions(self):
        permission_classes = (
            [IsAuthenticated] if self.request.method == "GET" else [IsAdminRole]
        )
        return [permission() for permission in permission_classes]

    def get(self, request, class_id=None):
        # ``class_id`` is retained as the URL kwarg for reverse compatibility.
        catalog_id = class_id
        if catalog_id:
            catalog = CatalogTypeAtendance.objects.filter(pk=catalog_id).first()
            if catalog is None:
                return Response({"error": "Attendance catalog item not found"}, status=404)
            serializer = AttendanceCatalogSerializer(catalog)
            return Response(serializer.data)

        catalog = CatalogTypeAtendance.objects.all()
        serializer = AttendanceCatalogSerializer(catalog, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AttendanceCatalogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def patch(self, request, class_id=None):
        catalog_id = class_id
        catalog = CatalogTypeAtendance.objects.filter(pk=catalog_id).first()
        if catalog is None:
            return Response({"error": "Attendance catalog item not found"}, status=404)

        serializer = AttendanceCatalogSerializer(
            catalog,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, class_id=None):
        catalog_id = class_id
        catalog = CatalogTypeAtendance.objects.filter(pk=catalog_id).first()
        if catalog is None:
            return Response({"error": "Attendance catalog item not found"}, status=404)

        try:
            catalog.delete()
        except (ProtectedError, RestrictedError):
            return Response(
                {"detail": "This attendance catalog item is in use and cannot be deleted."},
                status=409,
            )
        return Response(status=204)
