from rest_framework import serializers

from academics.models import ClassRoom, Subject
from academics.serializer import SubjectSerializer
from assignments.models import Assignment
from grades.models import GradingCriteria
from grades.serializer import GradingCriteriaSerializer


class AssignmentSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    grading_criteria = GradingCriteriaSerializer(read_only=True)
    class_room_id = serializers.PrimaryKeyRelatedField(source='class_room', read_only=True)

    class_room = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.all(),
        write_only=True,
    )
    subject_id = serializers.PrimaryKeyRelatedField(
        source='subject',
        queryset=Subject.objects.all(),
        write_only=True,
    )
    grading_criteria_id = serializers.PrimaryKeyRelatedField(
        source='grading_criteria',
        queryset=GradingCriteria.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Assignment
        fields = [
            'id',
            'class_room_id',
            'class_room',
            'subject',
            'subject_id',
            'grading_criteria',
            'grading_criteria_id',
            'title',
            'description',
            'due_date',
            'max_score',
            'created_at',
            'updated_at',
        ]
