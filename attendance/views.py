from datetime import date

from rest_framework.views import APIView
from rest_framework.response import Response
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
    def get(self, request,class_id=None,date=None,student_id=None):
        use_case = build_list_attendance_use_case()
        attendance_data = use_case.execute(
            class_id=str(class_id) if class_id else None,
            attendance_date=date,
            student_id=str(student_id) if student_id else None,
        )
        return Response(attendance_data)

    def post(self, request, class_id=None):
        if not class_id:
            return Response({"error": "Class ID is required"}, status=400)

        student_id = request.data.get("student")
        state_code_id = request.data.get("state_code")
        attendance_date = request.data.get("date")

        if not student_id or not state_code_id or not attendance_date:
            return Response(
                {"error": "student, state_code and date are required"},
                status=400,
            )

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
    def get(self, request):
        catalog = CatalogTypeAtendance.objects.all()
        serializer = AttendanceCatalogSerializer(catalog, many=True)
        return Response(serializer.data)

    def post(self, request):
        from attendance.models import CatalogTypeAtendance
        from .serializer import AttendanceCatalogSerializer
        serializer = AttendanceCatalogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


