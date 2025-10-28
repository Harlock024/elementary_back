from rest_framework import serializers
from .models import Student
from academics.serializer import EnrollmentSerializer

class StudentSerializer(serializers.ModelSerializer):
    enrollment = EnrollmentSerializer(read_only=True,many=True)

    class Meta:
        model = Student
        fields = ['id', 'first_name', 'second_name', 'last_name', 'enrollment_number', 'date_of_birth', 'gender', 'state','enrollment','created_at', 'updated_at'] 



