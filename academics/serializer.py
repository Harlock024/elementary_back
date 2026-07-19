from rest_framework import serializers

from staff.serializer import StaffSerializerNameOnly
from students.base_serializer import StudentSerializerNameOnly
from .models import AcademicPeriod, ClassRoom, Enrollment, SchoolGrade, Group, Subject
from academics.models import Group


class StudentActionSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    action = serializers.ChoiceField(choices=['promote', 'repeat', 'graduate'])


class TargetGroupSerializer(serializers.Serializer):
    school_grade_id = serializers.UUIDField()
    letter = serializers.CharField(max_length=5)


class PromotionInputSerializer(serializers.Serializer):
    source_classroom_id = serializers.UUIDField()
    target_period_id = serializers.UUIDField(required=False)
    period = serializers.CharField(max_length=20, required=False, write_only=True)
    students = StudentActionSerializer(many=True)
    target_group = TargetGroupSerializer(required=False, allow_null=True)

    def validate_students(self, value):
        ids = [item['student_id'] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("No pueden venir student_id duplicados.")
        return value

    def validate(self, data):
        needs_target_period = any(
            student['action'] in {'promote', 'repeat'}
            for student in data.get('students', [])
        )
        if needs_target_period and not data.get('target_period_id') and not data.get('period'):
            raise serializers.ValidationError(
                {'target_period_id': 'Selecciona el ciclo académico destino.'}
            )
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
    academic_period = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Enrollment
        fields = ['id', 'period', 'academic_period', 'state']

class EnrollmentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'group', 'period', 'academic_period', 'state', 'created_at', 'updated_at']


class AcademicPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicPeriod
        fields = [
            'id', 'name', 'start_date', 'end_date', 'status',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, attrs):
        start = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        if start and end and start >= end:
            raise serializers.ValidationError(
                {'end_date': 'La fecha final debe ser posterior a la fecha inicial.'}
            )
        return attrs

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
        enrollments = obj.enrollments.filter(state__in=('activo', 'active'))
        academic_period_id = self.context.get('academic_period_id')
        if academic_period_id:
            enrollments = enrollments.filter(academic_period_id=academic_period_id)
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
    group = serializers.SerializerMethodField()
    staff = StaffSerializerNameOnly(read_only=True)
    academic_period = AcademicPeriodSerializer(read_only=True)

    def get_group(self, obj):
        return GroupDetailSerializer(
            obj.group,
            context={**self.context, 'academic_period_id': obj.academic_period_id},
        ).data

    class Meta:
        model = ClassRoom
        fields = ['id', 'staff', 'group', 'academic_period', 'created_at', 'updated_at']



# Note: Enrollment.group.field.related_model.subjects.field.related_model
# is used to access the Subject model through the relationships defined in the Enrollment and Group models.
