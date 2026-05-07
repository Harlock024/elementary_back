from rest_framework import serializers

from academics.models import ClassRoom
from students import serializer
from .models import StudentGrade,CatalogTypeGrade
from academics.serializer import EnrollmentSerializer, SubjectNameOnlySerializer, SubjectSerializer
from students.serializer import StudentSerializerNameOnly


class GradingCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogTypeGrade
        fields = ['id', 'name', 'percentage', 'created_at', 'updated_at']   


class StudentGradeSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    student = StudentSerializerNameOnly(read_only=True)
    class_id = serializers.PrimaryKeyRelatedField(source='class_room',read_only=True)

    # Extra fields to write the related objects by their IDs
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
            'type_code',
            'score',
            'max_score',
            'description',
            'date',
            'created_at',
            'updated_at',
                ]






