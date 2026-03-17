from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .serializer import StaffSerializer
from staff.application.dto.staff_dto import CreateStaffCommand, UpdateStaffCommand
from staff.domain.exceptions.staff_exceptions import StaffNotFoundError
from staff.interfaces.http.staff_use_case_factory import (
    build_create_staff_use_case,
    build_delete_staff_use_case,
    build_list_staff_use_case,
    build_update_staff_use_case,
)
#hardcode
from .models import Staff
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import random
import string


class StaffView(APIView):
    def get(self, request):
        use_case = build_list_staff_use_case()
        return Response(use_case.execute())

    def post(self, request):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        if not first_name or not last_name:
            return Response({"error": "first_name and last_name are required"}, status=400)

        use_case = build_create_staff_use_case()
        command = CreateStaffCommand(first_name=first_name, last_name=last_name)

        try:
            data = use_case.execute(command)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)

        return Response(data)

    def put(self, request, pk):
        update_use_case = build_update_staff_use_case()

        try:
            command = UpdateStaffCommand(
                staff_id=str(pk),
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
                username=request.data.get("username"),
                role=request.data.get("role"),
            )
            staff_data = update_use_case.execute(command)
        except StaffNotFoundError:
            return Response({"error": "Staff not found."}, status=404)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        return Response(staff_data)

    def delete(self, request, pk):
        delete_use_case = build_delete_staff_use_case()

        try:
            delete_use_case.execute(str(pk))
        except StaffNotFoundError:
            return Response({"error": "Staff not found."}, status=404)
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



@api_view(['POST'])
def create_admin(request):
    admin = Staff(
        first_name=request.data.get("first_name"),
        last_name=request.data.get("last_name"),
        username=request.data.get("first_name").lower() + "_admin",
        role= "admin"
    )

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
