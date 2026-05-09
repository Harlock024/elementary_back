from rest_framework import serializers

from academics.models import ClassRoom
from academics.serializer import SubjectSerializer
from grades.models import GradingCriteria, StudentGrade
from students.serializer import StudentSerializerNameOnly


class GradingCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradingCriteria
        fields = ['id', 'name', 'class_room', 'percentage', 'is_attendance_based', 'created_at', 'updated_at']


class StudentGradeSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    student = StudentSerializerNameOnly(read_only=True)
    class_id = serializers.PrimaryKeyRelatedField(source='class_room', read_only=True)

    class_room = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.all(),
        write_only=True,
    )

    class Meta:
        model = StudentGrade
        fields = [
            'id',
            'student',
            'subject',
            'class_id',
            'class_room',
            'assignment',
            'score',
            'description',
            'date',
            'created_at',
            'updated_at',
        ]
