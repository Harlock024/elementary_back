from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Staff
from rest_framework.decorators import api_view
from .serializer import StaffSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import random
import string

class StaffView(APIView):
    def get(self, request):
        staffs = Staff.objects.all()
        serializer = StaffSerializer(staffs, many=True)
        return Response(serializer.data)

    def post(self, request):
    
        profesor = Staff(
                first_name=request.data.get('first_name'),
                last_name=request.data.get('last_name'),
                username=request.data.get('first_name').lower() + '_' + request.data.get('last_name').lower(),
                )  
        # generar password y asignarlo al is_profesor
        random_password =  generate_random_password()

        # Asignar la contraseña generada al campo password_professor no hasheada solo visible para administradores
        profesor.password_professor = random_password

        # Asignar la contraseña generada al usuario  y guardarla en el campo password hasheada
        profesor.set_password(random_password)


        profesor.is_teacher()
        profesor.save()
        serializer = StaffSerializer(profesor)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            staff = Staff.objects.get(pk=pk)
        except Staff.DoesNotExist:
            return Response({'error': 'Staff not found.'}, status=404)
        serializer = StaffSerializer(staff, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            staff = Staff.objects.get(pk=pk)
        except Staff.DoesNotExist:
            return Response({'error': 'Staff not found.'}, status=404)
        staff.delete()
        return Response(status=204)



class StaffProfileView(APIView):
    def get(self, request):
        serializer = StaffSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = StaffSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

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
def list_professors(request):
    professors = Staff.objects.filter(role='Teacher')
    serializer = StaffSerializer(professors, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_professor(request):
    
    profesor = Staff(
        first_name=request.data.get('first_name'),
        last_name=request.data.get('last_name'),
        username=request.data.get('first_name').lower() + '_' + request.data.get('last_name').lower(),
        )  

    # generar password y asignarlo al is_profesor
    random_password =  generate_random_password()

    # Asignar la contraseña generada al campo password_professor no hasheada solo visible para administradores
    profesor.password_professor = random_password

    # Asignar la contraseña generada al usuario  y guardarla en el campo password hasheada
    profesor.set_password(random_password)


    profesor.is_teacher()
    profesor.save()
    serializer = StaffSerializer(profesor)
    return Response(serializer.data)

@api_view(['DELETE'])
def  delete_professor(request, pk):
    try:
        professor = Staff.objects.get(pk=pk, role='profesor')
    except Staff.DoesNotExist:
        return Response({'error': 'Professor not found.'}, status=404)

    professor.delete()
    return Response({'message': 'Professor deleted successfully.'})


@api_view(['PUT'])
def update_professor(request, pk):
    try:
        professor = Staff.objects.get(pk=pk, role='profesor')
    except Staff.DoesNotExist:
        return Response({'error': 'Professor not found.'}, status=404)

    professor.first_name = request.data.get('first_name', professor.first_name)
    professor.last_name = request.data.get('last_name', professor.last_name)
    professor.username = request.data.get('username', professor.username)
    professor.save()
    serializer = StaffSerializer(professor)
    return Response(serializer.data)

def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    random_password = ''.join(random.choice(characters) for i in range(length))
    return random_password

@api_view(['POST'])
def create_admin(request):
    admin = Staff(
        first_name=request.data.get("first_name"),
        last_name=request.data.get("last_name"),
        username=request.data.get("first_name").lower() + "_admin",
    )
    admin.is_admin()
    admin.set_password(request.data.get("password"))
    admin.save()
    return Response({"message": "Admin user created."})


@api_view(['PATCH'])
def edit_professor(request,pk):
    try: 
        professor = Staff.objects.get(pk=pk, role='Teacher')
    except Staff.DoesNotExist:
        return Response({'error': 'Professor not found.'}, status=404)
    professor.first_name = request.data.get('first_name', professor.first_name)
    professor.last_name = request.data.get('last_name', professor.last_name)
    professor.username = request.data.get('username', professor.username)
    professor.save()
    serializer = StaffSerializer(professor)
    return Response(serializer.data)
