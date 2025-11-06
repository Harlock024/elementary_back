from rest_framework import serializers
from .models import Attendance,CatalogTypeAtendance
from students.serializer import StudentSerializerNameOnly

class AttendanceCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogTypeAtendance
        fields = ['code','description']

class AttendanceSerializer(serializers.ModelSerializer):
    students =  StudentSerializerNameOnly(read_only=True, source='student')
    state_code = AttendanceCatalogSerializer(read_only=True)
    class_id = serializers.PrimaryKeyRelatedField(source='class_room', read_only=True)
    class Meta:
        model = Attendance
        fields = ['id', 'date', 'class_id', 'students', 'state_code']
