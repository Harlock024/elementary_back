from datetime import date

from rest_framework.response import Response
from rest_framework.views import APIView

from students.application.dto.student_dto import CreateStudentCommand, UpdateStudentCommand
from students.domain.exceptions.student_exceptions import (
    GroupNotFoundError,
    StudentNotFoundError,
)
from students.interfaces.http.student_use_case_factory import (
    build_create_student_use_case,
    build_delete_student_use_case,
    build_get_student_detail_use_case,
    build_list_students_use_case,
    build_update_student_use_case,
)

from elementary_back.middleware import IsAdmin


class StudentViewSet(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk=None):
        list_students_use_case = build_list_students_use_case()
        get_student_use_case = build_get_student_detail_use_case()

        if pk:
            try:
                student = get_student_use_case.execute(str(pk))
            except StudentNotFoundError:
                return Response({"error": "Student not found"}, status=404)
            return Response(student)
        else:
            students = list_students_use_case.execute()
            return Response(students)

    def post(self, request):
        create_student_use_case = build_create_student_use_case()

        group_id = request.data.get("group_id")
        period = request.data.get("period")
        birth_date = request.data.get("date_of_birth")

        if group_id is None:
            return Response({"error": "group_id is required"}, status=400)
        if period is None:
            return Response({"error": "period is required"}, status=400)
        if birth_date is None:
            return Response({"error": "date_of_birth is required"}, status=400)

        try:
            command = CreateStudentCommand(
                first_name=request.data.get("first_name"),
                second_name=request.data.get("second_name"),
                last_name=request.data.get("last_name"),
                date_of_birth=date.fromisoformat(birth_date),
                gender=request.data.get("gender"),
                state=request.data.get("state"),
                group_id=str(group_id),
                period=period,
            )
            student_data = create_student_use_case.execute(command)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        except GroupNotFoundError:
            return Response({"error": "Group not found"}, status=404)
        return Response(student_data, status=201)

    def put(self, request, pk):
        update_use_case = build_update_student_use_case()

        birth_date = request.data.get("date_of_birth")
        try:
            command = UpdateStudentCommand(
                student_id=str(pk),
                first_name=request.data.get("first_name"),
                second_name=request.data.get("second_name"),
                last_name=request.data.get("last_name"),
                date_of_birth=date.fromisoformat(birth_date) if birth_date else None,
                gender=request.data.get("gender"),
                state=request.data.get("state"),
            )
            student_data = update_use_case.execute(command)
        except StudentNotFoundError:
            return Response({"error": "Student not found"}, status=404)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        return Response(student_data)

    def delete(self, request, pk):
        delete_use_case = build_delete_student_use_case()

        try:
            delete_use_case.execute(str(pk))
        except StudentNotFoundError:
            return Response({"error": "Student not found"}, status=404)
        return Response(status=204)

    def patch(self, request, pk):
        update_use_case = build_update_student_use_case()

        birth_date = request.data.get("date_of_birth")
        try:
            command = UpdateStudentCommand(
                student_id=str(pk),
                first_name=request.data.get("first_name"),
                second_name=request.data.get("second_name"),
                last_name=request.data.get("last_name"),
                date_of_birth=date.fromisoformat(birth_date) if birth_date else None,
                gender=request.data.get("gender"),
                state=request.data.get("state"),
            )
            student_data = update_use_case.execute(command)
        except StudentNotFoundError:
            return Response({"error": "Student not found"}, status=404)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        return Response(student_data)


