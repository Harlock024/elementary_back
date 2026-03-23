from asyncio import wait
from rest_framework import serializers
from .models import Student
from academics.serializer import EnrollmentSerializer, GroupSerializer,SchoolGradeNameOnlySerializer


class StudentSerializer(serializers.ModelSerializer):
    enrollments = EnrollmentSerializer(read_only=True, many=True)
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'second_name', 'last_name', 
                  'enrollment_number','date_of_birth', 'gender', 
                  'state',
                  'syncStatus',
                  'version',
                  'localUpdatedAt',
                  'enrollments',
                  'created_at', 
                  'updated_at'
                  ] 


class StudentSerializerNameOnly(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'first_name','last_name']

class StudentDetailSerializer(serializers.ModelSerializer):
    enrollments = EnrollmentSerializer(read_only=True, many=True)
    
    group = serializers.SerializerMethodField()
    
    def get_group(self, obj:Student):
        last_enrollment = obj.enrollments.order_by('-created_at').first()

        if last_enrollment and last_enrollment.group:
            return GroupSerializer(last_enrollment.group).data
        return None
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'second_name', 'last_name', 
                  'enrollment_number','date_of_birth', 'gender',
                                        'state', 'syncStatus', 'version', 'localUpdatedAt', 'group','enrollments']

