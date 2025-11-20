from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from attendance.models import Attendance, CatalogTypeAtendance
from .serializer import AttendanceSerializer,AttendanceCatalogSerializer
# Create your views here.


class AttendaceView(APIView):
    def get(self, request,class_id=None,date=None,student_id=None):
        if class_id: 
            attendance = Attendance.objects.filter(class_room_id=class_id)
            serializer = AttendanceSerializer(attendance, many=True)
            data = serializer.data
            return Response(data)

        elif class_id and date:
            attendance = Attendance.objects.filter(class_room_id=class_id, date=date)
            serializer = AttendanceSerializer(attendance, many=True)
            data = serializer.data
            return Response(data)
        elif student_id and date:
            attendance = Attendance.objects.filter(student_id=student_id, date=date)
            serializer = AttendanceSerializer(attendance, many=True)
            data = serializer.data
            return Response(data)
        elif not class_id:
            all_attendance = Attendance.objects.all()
            serializer = AttendanceSerializer(all_attendance, many=True)
            data = serializer.data
            return Response(data)



    def post(self, request, class_id=None):
        if class_id:
            serializer = AttendanceSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(class_room_id=class_id)
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        return Response({"error": "Class ID is required"}, status=400)

    def patch(self, request):
        if id:
            serializer = AttendanceSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        return Response({"error": "Class ID is required"}, status=400)

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


