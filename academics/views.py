from asyncio import wait
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from elementary_back.middleware import IsAdmin

from .models import Enrollment, SchoolGrade, Group, Subject
from .serializer import EnrollmentSerializer, SchoolGradeSerializer, GroupSerializer, SubjectSerializer

class SchoolGradeViewSet(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk=None):
        if pk:
            try:
                school_grade = SchoolGrade.objects.get(pk=pk)
            except SchoolGrade.DoesNotExist:
                return Response({"error": "School Grade not found"}, status=404)
            serializer = SchoolGradeSerializer(school_grade)
            return Response(serializer.data)
        else:
            school_grades = SchoolGrade.objects.all()
            serializer = SchoolGradeSerializer(school_grades, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = SchoolGradeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        try:
            school_grade = SchoolGrade.objects.get(pk=pk)
        except SchoolGrade.DoesNotExist:
            return Response({"error": "School Grade not found"}, status=404)

        serializer = SchoolGradeSerializer(school_grade, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)



class GroupViewSet(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk=None):
        if pk:
            try:
                group = Group.objects.get(pk=pk)
            except Group.DoesNotExist:
                return Response({"error": "Group not found"}, status=404)
            serializer = GroupSerializer(group)
            return Response(serializer.data)
        else:
            groups = Group.objects.all()
            serializer = GroupSerializer(groups, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    def put(self, request, pk):
        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response({"error": "Group not found"}, status=404)

        serializer = GroupSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class SubjectViewSet(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk=None):
        if pk:
            try:
                subject = Subject.objects.get(pk=pk)
            except Subject.DoesNotExist:
                return Response({"error": "Subject not found"}, status=404)
            serializer = SubjectSerializer(subject)
            return Response(serializer.data)
        else:
            subjects = Subject.objects.all()
            serializer = SubjectSerializer(subjects, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        try:
            subject = Subject.objects.get(pk=pk)
        except Subject.DoesNotExist:
            return Response({"error": "Subject not found"}, status=404)

        serializer = SubjectSerializer(subject, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


# en revision, posible conflicto con student viewset al crear matricula
class EnrollmentViewSet(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk=None):
        if pk:
            try:
                enrollment = Enrollment.objects.get(pk=pk)
            except Enrollment.DoesNotExist:
                return Response({"error": "Enrollment not found"}, status=404)
            serializer = EnrollmentSerializer(enrollment)
            return Response(serializer.data)
        else:
            enrollments = Enrollment.objects.all()
            serializer = EnrollmentSerializer(enrollments, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = EnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        try:
            enrollment = Enrollment.objects.get(pk=pk)
        except Enrollment.DoesNotExist:
            return Response({"error": "Enrollment not found"}, status=404)

        serializer = EnrollmentSerializer(enrollment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
