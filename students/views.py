from asyncio import wait
from .models import Student
from academics.models import Enrollment
from rest_framework.response import Response
from .serializer import StudentSerializer,StudentDetailSerializer
from rest_framework.views import  APIView

from elementary_back.middleware import IsAdmin

class StudentViewSet(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk=None):
        if pk:
            try:
                student = Student.objects.get(pk=pk)
            except Student.DoesNotExist:
                return Response({"error": "Student not found"}, status=404)
            serializer = StudentDetailSerializer(student)
            return Response({'students':serializer.data})
        else:
            students = Student.objects.all()
            serializer = StudentDetailSerializer(students, many=True)
            return Response({'students':serializer.data})


# create student with enrollment 
    def post(self, request):
        data = Student(
            first_name=request.data.get('first_name'),
            second_name=request.data.get('second_name'),
            last_name=request.data.get('last_name'),
            date_of_birth=request.data.get('date_of_birth'),
            gender=request.data.get('gender'),
            state =request.data.get('state'),
            )

        data.enrollment_number = Student.generate_enrollment_number()
        data.save()
        enrollment = Enrollment(
            student=data,
            group_id=request.data.get('group_id'),
            period=request.data.get('period'),
            state='active'
        )
        enrollment.save()
        student_serializer = StudentSerializer(data)
        return Response({"student ": student_serializer.data}, status=201)



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


