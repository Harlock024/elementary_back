from django.db.models.deletion import ProtectedError
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings as simplejwt_settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from elementary_back.middleware import IsAdmin
from staff.application.dto.staff_dto import CreateStaffCommand, UpdateStaffCommand
from staff.domain.exceptions.staff_exceptions import StaffNotFoundError
from staff.interfaces.http.staff_use_case_factory import (
    build_create_staff_use_case,
    build_delete_staff_use_case,
    build_list_staff_use_case,
    build_update_staff_use_case,
)

from .models import Staff
from .serializer import StaffProfileUpdateSerializer, StaffSerializer
from .throttles import LoginRateThrottle


SENSITIVE_ACCOUNT_FIELDS = {
    "username",
    "role",
    "password",
    "is_active",
    "is_staff",
    "is_superuser",
}
HISTORY_PROTECTED_DETAIL = (
    "No se puede eliminar este usuario porque está vinculado al historial académico."
)


class StaffView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        use_case = build_list_staff_use_case()
        return Response(use_case.execute())

    def post(self, request):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        password = request.data.get("password")
        if not first_name or not last_name or not password:
            return Response(
                {"error": "first_name, last_name and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        command = CreateStaffCommand(
            first_name=first_name,
            last_name=last_name,
            password=password,
            username=request.data.get("username") or None,
            role=request.data.get("role") or "Teacher",
        )

        try:
            data = build_create_staff_use_case().execute(command)
        except ValueError as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(data, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        if "password" in request.data:
            return Response(
                {"password": "Use a dedicated password reset flow."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user.pk == pk:
            forbidden = sorted(SENSITIVE_ACCOUNT_FIELDS.intersection(request.data.keys()))
            if forbidden:
                return Response(
                    {
                        field: "You cannot change this field on your own account."
                        for field in forbidden
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            command = UpdateStaffCommand(
                staff_id=str(pk),
                first_name=request.data.get("first_name"),
                last_name=request.data.get("last_name"),
                username=request.data.get("username"),
                role=request.data.get("role"),
            )
            staff_data = build_update_staff_use_case().execute(command)
        except StaffNotFoundError:
            return Response(
                {"error": "Staff not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(staff_data)

    def delete(self, request, pk):
        if request.user.pk == pk:
            return Response(
                {"error": "You cannot delete your own account."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            build_delete_staff_use_case().execute(str(pk))
        except StaffNotFoundError:
            return Response(
                {"error": "Staff not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except ProtectedError:
            return Response(
                {"detail": HISTORY_PROTECTED_DETAIL},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class StaffProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(StaffSerializer(request.user).data)

    def _update(self, request):
        serializer = StaffProfileUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(StaffSerializer(request.user).data)

    def put(self, request):
        return self._update(request)

    def patch(self, request):
        return self._update(request)


class StaffTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["username"] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update(StaffSerializer(self.user).data)
        return data


class StaffLoginView(TokenObtainPairView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]
    serializer_class = StaffTokenObtainPairSerializer


class StaffTokenRefreshView(TokenRefreshView):
    authentication_classes = []
    permission_classes = [AllowAny]


class StaffLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"refresh": "This field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh)
        except TokenError:
            return Response(
                {"refresh": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_user_id = token.get(simplejwt_settings.USER_ID_CLAIM)
        request_user_id = getattr(request.user, simplejwt_settings.USER_ID_FIELD)
        if str(token_user_id) != str(request_user_id):
            return Response(
                {"refresh": "This refresh token does not belong to the current user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token.blacklist()

        return Response(status=status.HTTP_204_NO_CONTENT)


class StaffChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        new_password_confirm = request.data.get("new_password_confirm")

        values = {
            "current_password": current_password,
            "new_password": new_password,
            "new_password_confirm": new_password_confirm,
        }
        invalid_fields = {
            field: "This field is required."
            for field, value in values.items()
            if not isinstance(value, str) or not value
        }
        if invalid_fields:
            return Response(invalid_fields, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.check_password(current_password):
            return Response(
                {"current_password": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if new_password != new_password_confirm:
            return Response(
                {"new_password_confirm": "Passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if current_password == new_password:
            return Response(
                {"new_password": "The new password must be different."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user=request.user)
        except ValidationError as exc:
            return Response(
                {"new_password": exc.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            request.user.set_password(new_password)
            request.user.save(update_fields=["password", "updated_at"])
            for outstanding_token in OutstandingToken.objects.filter(
                user=request.user
            ):
                BlacklistedToken.objects.get_or_create(token=outstanding_token)

        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAdmin])
def list_professors(request):
    professors = Staff.objects.filter(role="Teacher")
    return Response(StaffSerializer(professors, many=True).data)


def _create_legacy_staff(request, role):
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")
    password = request.data.get("password")
    if not first_name or not last_name or not password:
        return Response(
            {"error": "first_name, last_name and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    command = CreateStaffCommand(
        first_name=first_name,
        last_name=last_name,
        password=password,
        username=request.data.get("username") or None,
        role=role,
    )
    try:
        data = build_create_staff_use_case().execute(command)
    except ValueError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAdmin])
def create_professor(request):
    return _create_legacy_staff(request, role="Teacher")


@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_professor(request, pk):
    if request.user.pk == pk:
        return Response(
            {"error": "You cannot delete your own account."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        professor = Staff.objects.get(pk=pk, role="Teacher")
    except Staff.DoesNotExist:
        return Response(
            {"error": "Professor not found."}, status=status.HTTP_404_NOT_FOUND
        )

    try:
        professor.delete()
    except ProtectedError:
        return Response(
            {"detail": HISTORY_PROTECTED_DETAIL},
            status=status.HTTP_409_CONFLICT,
        )
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAdmin])
def create_admin(request):
    return _create_legacy_staff(request, role="Admin")


@api_view(["PATCH"])
@permission_classes([IsAdmin])
def edit_professor(request, pk):
    try:
        professor = Staff.objects.get(pk=pk, role="Teacher")
    except Staff.DoesNotExist:
        return Response(
            {"error": "Professor not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if request.user.pk == pk and "username" in request.data:
        return Response(
            {"username": "You cannot change your own username."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    professor.first_name = request.data.get("first_name", professor.first_name)
    professor.last_name = request.data.get("last_name", professor.last_name)
    professor.username = request.data.get("username", professor.username)
    professor.save()
    return Response(StaffSerializer(professor).data)
