from rest_framework import serializers
from .models import Student # Asume que el modelo está aquí

class StudentSerializerNameOnly(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'first_name']
