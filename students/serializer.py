from rest_framework import serializers
from .models import Student
from academics.serializer import EnrollmentSerializer, GroupSerializer


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
