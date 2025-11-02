from rest_framework import serializers
from .models import ClassRoom, Enrollment , SchoolGrade, Group, Subject
from staff.models import Staff
from academics.models import Group


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'group', 'period', 'state']


class SchoolGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolGrade
        fields = ['id', 'name', 'created_at', 'updated_at']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'letter', 'school_grade', 'created_at', 'updated_at']



class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'school_grade', 'created_at', 'updated_at']


class SubjectNameOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['name']

class ClassRoomSerializer(serializers.ModelSerializer):
    group = GroupSerializer(read_only=True) 
    class Meta:
        model = ClassRoom
        fields = ['id', 'staff', 'created_at', 'updated_at', 'group']

# Note: Enrollment.group.field.related_model.subjects.field.related_model
# is used to access the Subject model through the relationships defined in the Enrollment and Group models.

