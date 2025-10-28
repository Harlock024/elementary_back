from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import StudentGrade
from .serializer import StudentGradeSerializer

class GradeViewSet(APIView):

    def get(self, request, pk=None):
        if pk:
            try:
                grade = StudentGrade.objects.get(pk=pk)
            except StudentGrade.DoesNotExist:
                return Response({"error": "Grade not found"}, status=404)
            serializer = StudentGradeSerializer(grade)
            return Response(serializer.data)
        else:
            grades = StudentGrade.objects.all()
            serializer = StudentGradeSerializer(grades, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = StudentGradeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        try:
            grade = StudentGrade.objects.get(pk=pk)
        except StudentGrade.DoesNotExist:
            return Response({"error": "Grade not found"}, status=404)
        serializer = StudentGradeSerializer(grade, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            grade = StudentGrade.objects.get(pk=pk)
        except StudentGrade.DoesNotExist:
            return Response({"error": "Grade not found"}, status=404)
        grade.delete()
        return Response(status=204)
