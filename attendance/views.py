from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from academics.models import ClassRoom
from attendance.models import Attendance, CatalogTypeAtendance
from students.models import Student
from .serializer import AttendanceSerializer,AttendanceCatalogSerializer,AttendanceCreateUpdateSerializer
# Create your views here.


class AttendaceView(APIView):
    def get(self, request,class_id=None,date=None,student_id=None):
        
        if class_id and date:
            attendance = Attendance.objects.filter(class_room_id=class_id, date=date)
            serializer = AttendanceSerializer(attendance, many=True)
            data = serializer.data
            return Response(data)
        elif class_id: 
            attendance = Attendance.objects.filter(class_room_id=class_id)
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
            studentAttendace = Attendance.objects.filter(date=request.data.get("date"), student_id=request.data.get('student'))
            if studentAttendace.exists():
                return Response({"error": "Attendance for this student in this class already exists."}, status=400)
            
            student= Student.objects.filter(id=request.data.get('student'))
            if not student.exists():
                return Response({"error": "Student does not exist."}, status=400)

            catalogTypeAtendance= CatalogTypeAtendance.objects.filter(id=request.data.get('state_code'))
            if not catalogTypeAtendance.exists():
                return Response({"error": "State code does not exist."}, status=400)

            class_room = ClassRoom.objects.filter(id=class_id)
            if not class_room.exists():
                return Response({"error": "Class room does not exist."}, status=400)

            studentAttendace = Attendance(
                    class_room= class_room.first(),
                    student=student.first(),
                    date=request.data.get('date'),
                    state_code=catalogTypeAtendance.first()
            )
            serializer = AttendanceCreateUpdateSerializer(studentAttendace, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)
        return Response({"error": "Class ID is required"}, status=400)

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


