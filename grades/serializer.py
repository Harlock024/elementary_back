from rest_framework import serializers

from academics.models import ClassRoom
from academics.serializer import SubjectSerializer
from assignments.models import Assignment
from grades.models import GradingCriteria, StudentGrade
from students.serializer import StudentSerializerNameOnly


class GradingCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradingCriteria
        fields = ['id', 'name', 'class_room', 'percentage', 'is_attendance_based', 'created_at', 'updated_at']


class AssignmentInGradeSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'title', 'max_score', 'subject']


class StudentGradeSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    student = StudentSerializerNameOnly(read_only=True)
    class_id = serializers.PrimaryKeyRelatedField(source='class_room', read_only=True)
    assignment = AssignmentInGradeSerializer(read_only=True)

    class Meta:
        model = StudentGrade
        fields = [
            'id',
            'student',
            'subject',
            'class_id',
            'assignment',
            'score',
            'description',
            'date',
            'created_at',
            'updated_at',
        ]
