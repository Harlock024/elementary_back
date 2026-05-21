from rest_framework import serializers

from staff.serializer import StaffSerializerNameOnly
from students.base_serializer import StudentSerializerNameOnly
from .models import ClassRoom, Enrollment , SchoolGrade, Group, Subject
from academics.models import Group


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

