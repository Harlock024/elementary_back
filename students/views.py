from datetime import date

from django.db.models.deletion import ProtectedError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from academics.models import ClassRoom
from elementary_back.permissions import (
    can_access_classroom,
    can_access_student_classrooms,
    is_admin_user,
)
from students.application.dto.student_dto import CreateStudentCommand, UpdateStudentCommand
from students.domain.exceptions.student_exceptions import GroupNotFoundError, StudentNotFoundError
from students.interfaces.http.student_use_case_factory import (
    build_create_student_use_case,
    build_delete_student_use_case,
    build_get_student_detail_use_case,
    build_get_student_profile_use_case,
    build_list_students_by_classroom_use_case,
    build_list_students_by_group_use_case,
    build_list_students_use_case,
    build_update_student_use_case,
)


def _forbidden(detail: str) -> Response:
    return Response({"detail": detail}, status=403)


HISTORY_PROTECTED_DETAIL = (
    "No se puede eliminar este alumno porque forma parte del historial académico."
)


def _teacher_classroom_ids(user) -> list[str] | None:
    if is_admin_user(user):
        return None
    return [
        str(classroom_id)
        for classroom_id in ClassRoom.objects.filter(
            staff=user,
        ).values_list('id', flat=True)
    ]


class StudentViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id=None, pk=None):
        if group_id:
            owns_group = ClassRoom.objects.filter(
                group_id=group_id,
                staff=request.user,
            ).exists()
            if not is_admin_user(request.user) and not owns_group:
                return _forbidden("You do not have access to this group.")
            try:
                students = build_list_students_by_group_use_case().execute(str(group_id))
            except GroupNotFoundError:
                return Response({"error": "Group not found"}, status=404)
            return Response(students)

        if pk:
            if not is_admin_user(request.user) and not can_access_student_classrooms(
                request.user,
                pk,
            ):
                return _forbidden("You do not have access to this student.")
            try:
                student = build_get_student_detail_use_case().execute(
                    str(pk),
                    classroom_ids=_teacher_classroom_ids(request.user),
                )
            except StudentNotFoundError:
                return Response({"error": "Student not found"}, status=404)
            return Response(student)

        classroom_id = request.query_params.get("classroom_id")
        if classroom_id:
            if not can_access_classroom(request.user, classroom_id):
                return _forbidden("You do not have access to this classroom.")
            return Response(build_list_students_by_classroom_use_case().execute(classroom_id))

        if not is_admin_user(request.user):
            return _forbidden("Only administrators can list all students.")
        return Response(build_list_students_use_case().execute())

    def post(self, request):
        if not is_admin_user(request.user):
            return _forbidden("Only administrators can create students.")

        group_id = request.data.get("group_id")
        period = request.data.get("period")
        academic_period_id = request.data.get("academic_period_id") or request.data.get("academic_period")
        birth_date = request.data.get("date_of_birth")

        required = {
            "group_id": group_id,
            "period": period or academic_period_id,
            "date_of_birth": birth_date,
            "curp": request.data.get("curp"),
            "tutor_name": request.data.get("tutor_name"),
            "tutor_phone": request.data.get("tutor_phone"),
            "tutor_relationship": request.data.get("tutor_relationship"),
        }
        for field, value in required.items():
            if not value:
                return Response({"error": f"{field} is required"}, status=400)

        try:
            command = CreateStudentCommand(
                first_name=request.data.get("first_name"),
                second_name=request.data.get("second_name"),
                last_name=request.data.get("last_name"),
                curp=request.data.get("curp"),
                tutor_name=request.data.get("tutor_name"),
                tutor_phone=request.data.get("tutor_phone"),
                tutor_relationship=request.data.get("tutor_relationship"),
                date_of_birth=date.fromisoformat(birth_date),
                gender=request.data.get("gender"),
                state=request.data.get("state"),
                group_id=str(group_id),
                period=period,
                academic_period_id=str(academic_period_id) if academic_period_id else None,
            )
            return Response(build_create_student_use_case().execute(command), status=201)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        except GroupNotFoundError:
            return Response({"error": "Group not found"}, status=404)

    def put(self, request, pk):
        if not is_admin_user(request.user):
            return _forbidden("Only administrators can update students.")

        birth_date = request.data.get("date_of_birth")
        try:
            command = UpdateStudentCommand(
                student_id=str(pk),
                first_name=request.data.get("first_name"),
                second_name=request.data.get("second_name"),
                last_name=request.data.get("last_name"),
                curp=request.data.get("curp"),
                tutor_name=request.data.get("tutor_name"),
                tutor_phone=request.data.get("tutor_phone"),
                tutor_relationship=request.data.get("tutor_relationship"),
                date_of_birth=date.fromisoformat(birth_date) if birth_date else None,
                gender=request.data.get("gender"),
                state=request.data.get("state"),
                group_id=request.data.get("group_id"),
                period=request.data.get("period"),
                academic_period_id=str(request.data.get("academic_period_id") or request.data.get("academic_period"))
                if request.data.get("academic_period_id") or request.data.get("academic_period") else None,
            )
            return Response(build_update_student_use_case().execute(command))
        except StudentNotFoundError:
            return Response({"error": "Student not found"}, status=404)
        except GroupNotFoundError:
            return Response({"error": "Group not found"}, status=404)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)

    def patch(self, request, pk):
        return self.put(request, pk)

    def delete(self, request, pk):
        if not is_admin_user(request.user):
            return _forbidden("Only administrators can delete students.")
        try:
            build_delete_student_use_case().execute(str(pk))
        except StudentNotFoundError:
            return Response({"error": "Student not found"}, status=404)
        except ProtectedError:
            return Response({"detail": HISTORY_PROTECTED_DETAIL}, status=409)
        return Response(status=204)


class StudentProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        if not is_admin_user(request.user) and not can_access_student_classrooms(
            request.user,
            pk,
        ):
            return _forbidden("You do not have access to this student.")
        try:
            profile = build_get_student_profile_use_case().execute(
                str(pk),
                classroom_ids=_teacher_classroom_ids(request.user),
            )
        except StudentNotFoundError:
            return Response({"error": "Student not found"}, status=404)
        return Response(profile)
