from rest_framework import serializers
from .models import Student
from academics.models import Enrollment, Group
from academics.serializer import EnrollmentSerializer, GroupSerializer
from academics.models import Subject
from assignments.models import Assignment
from grades.models import StudentGrade


class StudentSerializer(serializers.ModelSerializer):
    enrollments = EnrollmentSerializer(read_only=True, many=True)

    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'second_name', 'last_name',
            'curp', 'tutor_name', 'tutor_phone', 'tutor_relationship',
            'enrollment_number', 'date_of_birth', 'gender', 'state',
            'enrollments', 'created_at', 'updated_at',
        ]


class StudentSerializerNameOnly(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name']


class StudentDetailSerializer(serializers.ModelSerializer):
    enrollments = EnrollmentSerializer(read_only=True, many=True)
    group = serializers.SerializerMethodField()

    def get_group(self, obj: Student):
        active_enrollment = obj.enrollments.filter(state='activo').order_by('-created_at').first()
        if active_enrollment and active_enrollment.group:
            return GroupSerializer(active_enrollment.group).data
        return None

    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'second_name', 'last_name',
            'curp', 'tutor_name', 'tutor_phone', 'tutor_relationship',
            'enrollment_number', 'date_of_birth', 'gender', 'state',
            'group', 'enrollments',
        ]


# --- Profile serializers ---

class _SubjectInProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']


class _AssignmentInProfileSerializer(serializers.ModelSerializer):
    subject = _SubjectInProfileSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = ['id', 'title', 'max_score', 'subject']


class _GradeInProfileSerializer(serializers.ModelSerializer):
    assignment = _AssignmentInProfileSerializer(read_only=True)

    class Meta:
        model = StudentGrade
        fields = ['id', 'score', 'created_at', 'assignment']


class _GroupInEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'letter']


class _EnrollmentInProfileSerializer(serializers.ModelSerializer):
    group = _GroupInEnrollmentSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'period', 'group']


class StudentProfileSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()
    enrollments = _EnrollmentInProfileSerializer(many=True, read_only=True)
    tutor = serializers.SerializerMethodField()
    grades = _GradeInProfileSerializer(many=True, read_only=True)

    def get_group(self, obj: Student):
        active = next((e for e in obj.enrollments.all() if e.state == 'activo'), None)
        if not active or not active.group:
            return None
        g = active.group
        return {
            'id': str(g.id),
            'letter': g.letter,
            'school_grade': {'id': str(g.school_grade.id), 'name': g.school_grade.name},
        }

    def get_tutor(self, obj: Student):
        return {
            'name': obj.tutor_name,
            'relationship': obj.tutor_relationship,
            'phone': obj.tutor_phone,
        }

    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'second_name', 'last_name',
            'gender', 'date_of_birth', 'state', 'enrollment_number', 'curp',
            'group', 'enrollments', 'tutor', 'grades',
        ]
