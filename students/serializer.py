from rest_framework import serializers
from .models import Student
from academics.serializer import EnrollmentSerializer



class StudentSerializer(serializers.ModelSerializer):
    enrollments = EnrollmentSerializer(read_only=True, many=True)
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'second_name', 'last_name', 
                  'enrollment_number','date_of_birth', 'gender', 
                  'state',
                  'enrollments',
                  'created_at', 
                  'updated_at'
                  ] 

class StudentSerializerNameOnly(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'first_name']



