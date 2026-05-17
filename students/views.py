from datetime import date

from rest_framework.response import Response
from rest_framework.views import APIView

from elementary_back.middleware import IsAdmin
from students.application.dto.student_dto import CreateStudentCommand, UpdateStudentCommand
from students.domain.exceptions.student_exceptions import GroupNotFoundError, StudentNotFoundError
from students.interfaces.http.student_use_case_factory import (
    build_create_student_use_case,
    build_delete_student_use_case,
    build_get_student_detail_use_case,
    build_list_students_use_case,
    build_list_students_by_group_use_case,
    build_update_student_use_case,
)
   


class StudentViewSet(APIView):
    permission_classes = [IsAdmin]
    
    def get(self, request,group_id=None, pk=None):
        if group_id:
            try:
                students = build_list_students_by_group_use_case().execute(str(group_id))
            except GroupNotFoundError:
                return Response({"error": "Group not found"}, status=404)
            return Response(students)
        if pk:
            try:
                student = build_get_student_detail_use_case().execute(str(pk))
            except StudentNotFoundError:
                return Response({"error": "Student not found"}, status=404)
            return Response(student)
        return Response(build_list_students_use_case().execute())

    def post(self, request):
        group_id = request.data.get("group_id")
        period = request.data.get("period")
        birth_date = request.data.get("date_of_birth")

        required = {"group_id": group_id, "period": period, "date_of_birth": birth_date,
                    "curp": request.data.get("curp"),
                    "tutor_name": request.data.get("tutor_name"),
                    "tutor_phone": request.data.get("tutor_phone"),
                    "tutor_relationship": request.data.get("tutor_relationship")}
        for field, value in required.items():
            if not value:
                return Response({"error": f"{field} is required"}, status=400)

        try:
            command = CreateStudentCommand(
                first_name=request.data.get("first_name"),
                second_name=request.data.get("second_name"),
                last_name=request.data.get("last_name"),
                curp=request.data.get("curp"),
                tutor_name=request.data.get("tutor_name"),
                tutor_phone=request.data.get("tutor_phone"),
                tutor_relationship=request.data.get("tutor_relationship"),
                date_of_birth=date.fromisoformat(birth_date),
                gender=request.data.get("gender"),
                state=request.data.get("state"),
                group_id=str(group_id),
                period=period,
            )
            return Response(build_create_student_use_case().execute(command), status=201)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        except GroupNotFoundError:
            return Response({"error": "Group not found"}, status=404)

    def put(self, request, pk):
        birth_date = request.data.get("date_of_birth")
        try:
            command = UpdateStudentCommand(
                student_id=str(pk),
                first_name=request.data.get("first_name"),
                second_name=request.data.get("second_name"),
                last_name=request.data.get("last_name"),
                curp=request.data.get("curp"),
                tutor_name=request.data.get("tutor_name"),
                tutor_phone=request.data.get("tutor_phone"),
                tutor_relationship=request.data.get("tutor_relationship"),
                date_of_birth=date.fromisoformat(birth_date) if birth_date else None,
                gender=request.data.get("gender"),
                state=request.data.get("state"),
            )
            return Response(build_update_student_use_case().execute(command))
        except StudentNotFoundError:
            return Response({"error": "Student not found"}, status=404)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)

    def patch(self, request, pk):
        return self.put(request, pk)

    def delete(self, request, pk):
        try:
            build_delete_student_use_case().execute(str(pk))
        except StudentNotFoundError:
            return Response({"error": "Student not found"}, status=404)
        return Response(status=204)


class StudentEnrrolmentView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        period = request.data.get("period")
        state = request.data.get("state")

        try:
            command = UpdateEnrollmentCommand(
                student_id=str(pk),
                period=period,
                state=state,
            )
            return Response(build_update_enrollment_use_case().execute(command))
        except StudentNotFoundError:
            return Response({"error": "Student not found"}, status=404)
        except GroupNotFoundError:
            return Response({"error": "Group not found"}, status=404)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)