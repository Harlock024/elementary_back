from rest_framework import serializers

from students import serializer
from .models import StudentGrade, CatalogTypeGrade
from academics.serializer import EnrollmentSerializer, SubjectNameOnlySerializer
from students.serializer import StudentSerializerNameOnly

class StudentGradeSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    student = StudentSerializerNameOnly(read_only=True)
    # type_code = serializers.StringRelatedField()
    type_code_name = serializers.CharField(source='type_code.code', read_only=True)
    class_id = serializers.PrimaryKeyRelatedField(source='class_room',read_only=True)
    class Meta:
        model = StudentGrade
        fields = [
            'id',
            'student',
            'subject_name',
            'class_id',
            'type_code_name',
            'score',
            'max_score',
            'description',
            'created_at',
            'updated_at',
                ]

class CatalogTypeGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogTypeGrade
        fields = ['id', 'code', 'description', 'created_at', 'updated_at']





