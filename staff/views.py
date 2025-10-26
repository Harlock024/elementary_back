from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.schemas.coreapi import serializers
from .models import Staff
from rest_framework.decorators import api_view, permission_classes
from .serializer import StaffSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class StaffTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['role'] = user.role
        token['username'] = user.username
        return token


    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = StaffSerializer(self.user).data
        for k, v in serializer.items():
            data[k] = v
            print(k,":", v)
        return data




class StaffLoginView(TokenObtainPairView):
    serializer_class = StaffTokenObtainPairSerializer


@api_view(['GET'])
def index(request):
    return Response("Hello, world. You're at the staff index.")


@api_view(['POST'])
@permission_classes([AllowAny]) 
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')


    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=400)
    user = authenticate(username=username, password=password)

    if user is not None:
        serializer = StaffSerializer(user)
        return Response({"message": "Login successful", "user": serializer.data})
    else:
        return Response({'error': 'Invalid credentials.'}, status=401)



@api_view(['GET'])
def list_professors(request):
    professors = Staff.objects.filter(role='profesor')
    serializer = StaffSerializer(professors, many=True)
    return Response({'professors': serializer.data})


@api_view(['POST'])
def create_professor(request):
    
    profesor = Staff(
        username=request.data.get('username'),
        first_name=request.data.get('first_name'),
        last_name=request.data.get('last_name')
        )
    profesor.set_password(request.data.get('password'))
    profesor.is_profesor()
    profesor.save()
    serializer = StaffSerializer(profesor)
    return Response(serializer.data)

