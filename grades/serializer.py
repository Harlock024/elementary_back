from rest_framework import serializers
from .models import StudentGrade
from academics.serializer import EnrollmentSerializer, SubjectSerializer
from students.serializer import StudentSerializer
class StudentGradeSerializer(serializers.ModelSerializer):
    enrollment = EnrollmentSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    student = StudentSerializer(read_only=True)

    class Meta:
        model = StudentGrade
        fields = [
            'id',
            'student',
            'class_room',
            'type_code',
            'score',
            'max_score',
            'description',
            'created_at',
            'updated_at',
            'enrollment',
            'subject',
                ]




