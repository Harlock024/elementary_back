from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from attendance.models import Attendance
from .serializer import AttendanceSerializer
# Create your views here.



class AttendaceView(APIView):
    def get(self, request,class_id=None):
        if class_id: 
            attendance = Attendance.objects.filter(class_room_id=class_id)
            serializer = AttendanceSerializer(attendance, many=True)
            data = serializer.data
            return Response(data)
    
        elif not class_id:
            all_attendance = Attendance.objects.all()
            serializer = AttendanceSerializer(all_attendance, many=True)
            data = serializer.data
            return Response(data)

