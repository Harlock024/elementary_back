from asyncio import wait
from django.http import request
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from students.models import Student
from academics.models import ClassRoom
from .models import StudentGrade,CatalogTypeGrade
from .serializer import StudentGradeSerializer, CatalogTypeGradeSerializer


class GradeViewSet(APIView):
    def get(self, request, class_room_id=None, pk=None):
        if pk:
            try:
                grade = StudentGrade.objects.get(pk=pk)
            except StudentGrade.DoesNotExist:
                return Response({"error": "Grade not found"}, status=404)
            serializer = StudentGradeSerializer(grade)
            return Response(serializer.data)
        elif class_room_id:
            grades = StudentGrade.objects.filter(class_room__id=class_room_id)
            serializer = StudentGradeSerializer(grades, many=True)
            return Response(serializer.data)
        else:
            grades = StudentGrade.objects.all()
            serializer = StudentGradeSerializer(grades, many=True)
            return Response(serializer.data)

    def post(self, request):
        try: 
            student_id = request.data.get("student")

            student = Student.objects.get(pk=student_id)
                
        except Student.DoesNotExist:
            return Response({"error":"Student not found"},status=404)
       
        try:
            class_room_id = request.data.get("class_room")
            class_room = ClassRoom.objects.get(pk=class_room_id)
        except ClassRoom.DoesNotExist:
            return Response({"error":"ClassRoom not found"},status=404)
        try:
            type_code_id = request.data.get("type_code")
            catalog_type = CatalogTypeGrade.objects.get(pk=type_code_id)
        except CatalogTypeGrade.DoesNotExist:
            return Response({"error":"Catalog Type not found"},status=404)

        student_grade_data = StudentGrade(
        student=student,
        class_room=class_room,
        score=request.data.get('score'),
        max_score=request.data.get('max_score'),
        description=request.data.get('description'),
        type_code=catalog_type
        )
        serializer = StudentGradeSerializer(student_grade_data, data=request.data)
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



class GradeCatalogViewSet(APIView):
    def get(self, request):

        catalog_types = CatalogTypeGrade.objects.all()
        serializer = CatalogTypeGradeSerializer(catalog_types, many=True)
        return Response(serializer.data)

    def post(self, request):

        serializer = CatalogTypeGradeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):

        try:
            catalog_type = CatalogTypeGrade.objects.get(pk=pk)
        except CatalogTypeGrade.DoesNotExist:
            return Response({"error": "Catalog Type not found"}, status=404)
        serializer = CatalogTypeGradeSerializer(catalog_type, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        from .models import CatalogTypeGrade

        try:
            catalog_type = CatalogTypeGrade.objects.get(pk=pk)
        except CatalogTypeGrade.DoesNotExist:
            return Response({"error": "Catalog Type not found"}, status=404)
        catalog_type.delete()
        return Response(status=204)


