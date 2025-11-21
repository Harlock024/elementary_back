from rest_framework import serializers

import students
from .models import Attendance,CatalogTypeAtendance
from students.serializer import StudentSerializerNameOnly

class AttendanceCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogTypeAtendance
        fields = ['id','code','description']

class AttendanceSerializer(serializers.ModelSerializer):
    student =  StudentSerializerNameOnly(read_only=True)
    state_code = AttendanceCatalogSerializer(read_only=True)
    class_id = serializers.PrimaryKeyRelatedField(source='class_room', read_only=True)
    class Meta:
        model = Attendance
        fields = ['id', 'date', 'class_id', 'student', 'state_code']


class AttendanceCreateUpdateSerializer(serializers.ModelSerializer):
    student =  StudentSerializerNameOnly(read_only=True)
    state_code = AttendanceCatalogSerializer(read_only=True)
    class Meta:
        model = Attendance
        fields = ['id', 'date', 'class_room', 'student', 'state_code']

