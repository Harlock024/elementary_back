from rest_framework import serializers

from staff.serializer import StaffSerializerNameOnly
from students.base_serializer import StudentSerializerNameOnly
from .models import ClassRoom, Enrollment , SchoolGrade, Group, Subject
from academics.models import Group


class StudentActionSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    action = serializers.ChoiceField(choices=['promote', 'repeat', 'graduate'])


class TargetGroupSerializer(serializers.Serializer):
    school_grade_id = serializers.UUIDField()
    letter = serializers.CharField(max_length=5)


class PromotionInputSerializer(serializers.Serializer):
    source_classroom_id = serializers.UUIDField()
    period = serializers.CharField(max_length=20)
    students = StudentActionSerializer(many=True)
    target_group = TargetGroupSerializer(required=False, allow_null=True)

    def validate_students(self, value):
        ids = [item['student_id'] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("No pueden venir student_id duplicados.")
        return value

    def validate(self, data):
        has_promotes = any(s['action'] == 'promote' for s in data.get('students', []))
        if has_promotes and not data.get('target_group'):
            raise serializers.ValidationError(
                {"target_group": "target_group es requerido cuando hay alumnos con action 'promote'."}
            )
        return data


class PromotionOutputSerializer(serializers.Serializer):
    promoted = serializers.IntegerField()
    repeated = serializers.IntegerField()
    graduated = serializers.IntegerField()
    target_group_id = serializers.UUIDField(allow_null=True)
    target_classroom_id = serializers.UUIDField(allow_null=True)


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'period', 'state']

class EnrollmentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'group', 'period', 'state', 'created_at', 'updated_at']

class SchoolGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolGrade
        fields = ['id', 'name', 'created_at', 'updated_at']


# school grade just name
class SchoolGradeNameOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolGrade
        fields = ['id','name']

class GroupSerializer(serializers.ModelSerializer):
    school_grade= SchoolGradeNameOnlySerializer(read_only=True)
    class Meta:
        model = Group
        fields = ['id', 'letter', 'school_grade', 'created_at', 'updated_at']

class GroupDetailSerializer(GroupSerializer):
    students = serializers.SerializerMethodField()

    class Meta(GroupSerializer.Meta):
        fields = GroupSerializer.Meta.fields + ['students']

    def get_students(self, obj: Group) -> list:
        enrollments = obj.enrollments.filter(state='activo')
        students = [e.student for e in enrollments]
        return StudentSerializerNameOnly(students, many=True).data

class SubjectSerializer(serializers.ModelSerializer):
    school_grade = SchoolGradeNameOnlySerializer(read_only=True)
    class Meta:
        model = Subject
        fields = ['id', 'name','school_grade','description','created_at', 'updated_at']

class SubjectDetailSerializer(serializers.ModelSerializer):
    school_grade = SchoolGradeSerializer(read_only=True)
    class Meta:
        model = Subject
        fields = ['id', 'name', 'school_grade', 'created_at', 'updated_at']

class SubjectNameOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['name']

class ClassRoomSerializer(serializers.ModelSerializer):
    group = GroupDetailSerializer(read_only=True)
    staff = StaffSerializerNameOnly(read_only=True)
    class Meta:
        model = ClassRoom
        fields = ['id', 'staff', 'group', 'created_at', 'updated_at']



# Note: Enrollment.group.field.related_model.subjects.field.related_model
# is used to access the Subject model through the relationships defined in the Enrollment and Group models.

