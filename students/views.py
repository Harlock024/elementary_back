from datetime import date

from .models import Student
from rest_framework.response import Response
from .serializer import StudentSerializer
from rest_framework.views import  APIView
from students.application.dto.student_dto import CreateStudentCommand
from students.domain.exceptions.student_exceptions import (
    GroupNotFoundError,
    StudentNotFoundError,
)
from students.interfaces.http.student_use_case_factory import (
    build_create_student_use_case,
    build_get_student_detail_use_case,
    build_list_students_use_case,
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

# create student with enrollment 
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
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

        student.delete()
        return Response(status=204)
    
    def patch(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=404)

        serializer = StudentSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


