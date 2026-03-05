from datetime import date

from rest_framework.views import APIView
from rest_framework.response import Response
from attendance.application.dto.attendance_dto import CreateAttendanceCommand
from attendance.domain.exceptions.attendance_exceptions import (
    AttendanceAlreadyExistsError,
    ClassRoomNotFoundError,
    StateCodeNotFoundError,
    StudentNotFoundForAttendanceError,
)
from attendance.interfaces.http.attendance_use_case_factory import (
    build_create_attendance_use_case,
    build_list_attendance_use_case,
)
from attendance.models import Attendance, CatalogTypeAtendance
from .serializer import AttendanceCatalogSerializer, AttendanceCreateUpdateSerializer
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
        if id:
            attendance = Attendance.objects.filter(id=id)
            if not attendance.exists():
                return Response({"error": "Attendance record does not exist."}, status=400)

            catalogTypeAtendance= CatalogTypeAtendance.objects.filter(id=request.data.get('state_code'))
            if not catalogTypeAtendance.exists():
                return Response({"error": "State code does not exist."}, status=400)

            attendance_record = attendance.first()
            attendance_record.state_code = catalogTypeAtendance.first()
            attendance_record.save()

            serializer = AttendanceCreateUpdateSerializer(attendance_record, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

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


