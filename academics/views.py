from django.db.models.deletion import ProtectedError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from academics.application.dto.academics_dto import (
    PromoteStudentsCommand,
    StudentActionItem,
    TargetGroupData,
    UpdateClassRoomCommand,
    UpdateEnrollmentCommand,
    UpdateGroupCommand,
    UpdateSubjectCommand,
)
from academics.application.dto.school_grade_dto import (
    CreateSchoolGradeCommand,
    UpdateSchoolGradeCommand,
)
from academics.domain.exceptions.academics_exceptions import (
    ClassRoomHistoryConflictError,
    ClassRoomNotFoundError,
    EnrollmentNotFoundError,
    GroupNotFoundError,
    PromotionError,
    SubjectNotFoundError,
)
from academics.domain.exceptions.school_grade_exceptions import SchoolGradeNotFoundError
from academics.interfaces.http.academics_use_case_factory import (
    build_delete_classroom_use_case,
    build_update_classroom_use_case,
    build_list_enrollments_use_case,
    build_update_enrollment_use_case,
    build_delete_enrollment_use_case,
    build_update_group_use_case,
    build_delete_group_use_case,
    build_update_subject_use_case,
    build_delete_subject_use_case,
    build_execute_promotion_use_case,
)
from academics.interfaces.http.school_grade_use_case_factory import (
    build_create_school_grade_use_case,
    build_get_school_grade_use_case,
    build_list_school_grades_use_case,
    build_update_school_grade_use_case,
)
from elementary_back.middleware import IsAdmin
from elementary_back.permissions import (
    can_access_classroom,
    is_admin_user,
    is_teacher_user,
)
from staff.models import Staff

from .models import ClassRoom, Enrollment, Group, SchoolGrade, Subject
from .serializer import (
    ClassRoomSerializer,
    EnrollmentSerializer,
    GroupDetailSerializer,
    GroupSerializer,
    PromotionInputSerializer,
    PromotionOutputSerializer,
    SubjectSerializer,
)


HISTORY_PROTECTED_DETAIL = (
    "No se puede eliminar este registro porque forma parte del historial académico."
)


class SchoolGradeViewSet(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk=None):
        get_school_grade_use_case = build_get_school_grade_use_case()
        list_school_grades_use_case = build_list_school_grades_use_case()

        if pk:
            try:
                school_grade = get_school_grade_use_case.execute(str(pk))
            except SchoolGradeNotFoundError:
                return Response({"error": "School Grade not found"}, status=404)
            return Response(school_grade)
        else:
            return Response(list_school_grades_use_case.execute())

    def post(self, request):
        name = request.data.get("name")
        if name is None:
            return Response({"error": "name is required"}, status=400)

        use_case = build_create_school_grade_use_case()
        command = CreateSchoolGradeCommand(name=name)
        try:
            data = use_case.execute(command)
            return Response(data, status=201)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)

    def put(self, request, pk):
        update_use_case = build_update_school_grade_use_case()

        try:
            command = UpdateSchoolGradeCommand(
                school_grade_id=str(pk),
                name=request.data.get("name"),
            )
            data = update_use_case.execute(command)
        except SchoolGradeNotFoundError:
            return Response({"error": "School Grade not found"}, status=404)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        return Response(data)

    def patch(self, request, pk):
        update_use_case = build_update_school_grade_use_case()

        try:
            command = UpdateSchoolGradeCommand(
                school_grade_id=str(pk),
                name=request.data.get("name"),
            )
            data = update_use_case.execute(command)
        except SchoolGradeNotFoundError:
            return Response({"error": "School Grade not found"}, status=404)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        return Response(data)


class GroupViewSet(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, pk=None):
        if pk:
            try:
                group = Group.objects.get(pk=pk)
            except Group.DoesNotExist:
                return Response({"error": "Group not found"}, status=404)
            serializer = GroupDetailSerializer(group)
            return Response(serializer.data)
        else:
            groups = Group.objects.all()
            serializer = GroupDetailSerializer(groups, many=True)
            return Response(serializer.data)

    def post(self, request):
        school_grade = SchoolGrade.objects.get(pk=request.data.get("school_grade"))
        if not school_grade.DoesNotExist:
            return Response({"error": "School Grade not found"}, status=404)
        data = Group(
            letter=request.data.get("letter"),
            school_grade=school_grade,
        )
        serializer = GroupSerializer(data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        update_use_case = build_update_group_use_case()

        try:
            command = UpdateGroupCommand(
                group_id=str(pk),
                letter=request.data.get("letter"),
                school_grade_id=str(request.data.get("school_grade"))
                if request.data.get("school_grade")
                else None,
            )
            data = update_use_case.execute(command)
        except GroupNotFoundError:
            return Response({"error": "Group not found"}, status=404)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        return Response(data)

    def patch(self, request, pk):
        update_use_case = build_update_group_use_case()

        try:
            command = UpdateGroupCommand(
                group_id=str(pk),
                letter=request.data.get("letter"),
                school_grade_id=str(request.data.get("school_grade"))
                if request.data.get("school_grade")
                else None,
            )
            data = update_use_case.execute(command)
        except GroupNotFoundError:
            return Response({"error": "Group not found"}, status=404)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        return Response(data)
    
    def delete(self, request, pk):
        delete_use_case = build_delete_group_use_case()
        try:
            delete_use_case.execute(str(pk))
        except GroupNotFoundError:
            return Response({"error": "Group not found"}, status=404)
        except ProtectedError:
            return Response({"detail": HISTORY_PROTECTED_DETAIL}, status=409)
        return Response(status=204)


class SubjectViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, class_id=None):
        if pk:
            try:
                subject = Subject.objects.get(pk=pk)
            except Subject.DoesNotExist:
                return Response({"error": "Subject not found"}, status=404)
            serializer = SubjectSerializer(subject)
            return Response(serializer.data)
        elif class_id:
            if not can_access_classroom(request.user, class_id):
                return Response(
                    {"detail": "You do not have access to this classroom."},
                    status=403,
                )
            try:
                classroom_group = ClassRoom.objects.get(pk=class_id).group
            except ClassRoom.DoesNotExist:
                return Response({"error": "ClassRoom not found"}, status=404)
            subjects = Subject.objects.filter(school_grade=classroom_group.school_grade)
            serializer = SubjectSerializer(subjects, many=True)
            return Response(serializer.data)
        else:
            subjects = Subject.objects.all()
            serializer = SubjectSerializer(subjects, many=True)
            return Response(serializer.data)

    def post(self, request):
        if not is_admin_user(request.user):
            return Response({"detail": "Only administrators can create subjects."}, status=403)
        try:
            school_grade = SchoolGrade.objects.get(pk=request.data.get("school_grade"))
        except (SchoolGrade.DoesNotExist, ValueError):
            return Response({"error": "School Grade not found"}, status=404)
        data = Subject(
            name=request.data.get("name"),
            school_grade=school_grade,
            description=request.data.get("description"),
        )
        serializer = SubjectSerializer(data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        if not is_admin_user(request.user):
            return Response({"detail": "Only administrators can update subjects."}, status=403)
        update_use_case = build_update_subject_use_case()

        try:
            command = UpdateSubjectCommand(
                subject_id=str(pk),
                name=request.data.get("name"),
                description=request.data.get("description"),
                school_grade_id=str(request.data.get("school_grade"))
                if request.data.get("school_grade")
                else None,
            )
            data = update_use_case.execute(command)
        except SubjectNotFoundError:
            return Response({"error": "Subject not found"}, status=404)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        return Response(data)

    def patch(self, request, pk):
        if not is_admin_user(request.user):
            return Response({"detail": "Only administrators can update subjects."}, status=403)
        update_use_case = build_update_subject_use_case()

        try:
            command = UpdateSubjectCommand(
                subject_id=str(pk),
                name=request.data.get("name"),
                description=request.data.get("description"),
                school_grade_id=str(request.data.get("school_grade"))
                if request.data.get("school_grade")
                else None,
            )
            data = update_use_case.execute(command)
        except SubjectNotFoundError:
            return Response({"error": "Subject not found"}, status=404)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        return Response(data)
    
    def delete(self, request, pk):
        if not is_admin_user(request.user):
            return Response({"detail": "Only administrators can delete subjects."}, status=403)
        delete_use_case = build_delete_subject_use_case()
        try:
            delete_use_case.execute(str(pk))
        except SubjectNotFoundError:
            return Response({"error": "Subject not found"}, status=404)
        except ProtectedError:
            return Response({"detail": HISTORY_PROTECTED_DETAIL}, status=409)
        return Response(status=204)


class EnrollmentViewSet(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, student_id=None, pk=None):
        staff = self.request.user
        if pk:
            try:
                enrollment = Enrollment.objects.get(pk=pk)
            except Enrollment.DoesNotExist:
                return Response({"error": "Enrollment not found"}, status=404)
            serializer = EnrollmentSerializer(enrollment)
            return Response(serializer.data)
        elif student_id:
            enrollments = Enrollment.objects.filter(student_id=student_id)
            serializer = EnrollmentSerializer(enrollments, many=True)
            return Response(serializer.data)
        elif request.query_params.get('group'):
            enrollments = Enrollment.objects.filter(
                group_id=request.query_params['group'],
                state='activo',
            )
            serializer = EnrollmentSerializer(enrollments, many=True)
            return Response(serializer.data)
        elif  staff.role == "Superuser" or staff.role == "Principal":
            enrollments = Enrollment.objects.all()
            serializer = EnrollmentSerializer(enrollments, many=True)
            return Response(serializer.data)
        elif staff.role == "Admin":
            enrollments = Enrollment.objects.filter(state="activo")
            serializer = EnrollmentSerializer(enrollments, many=True)   
            return Response(serializer.data)
        else:
            return Response(
                {"detail": "You do not have permission to access this resource."},
                status=403,
            )

    def post(self, request):
        group = Group.objects.get(pk=request.data.get("group"))
        if not group:
            return Response({"error": "Group not found"}, status=404)
        data = Enrollment(
            student_id=request.data.get("student"),
            group=group,
            period=request.data.get("period"),
            state=request.data.get("state"),
        )
        serializer = EnrollmentSerializer(data, data=request.data)
        if serializer.is_valid():            
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        update_use_case = build_update_enrollment_use_case()

        try:
            command = UpdateEnrollmentCommand(
                enrollment_id=str(pk),
                student_id=str(request.data.get("student"))
                if request.data.get("student")
                else None,
                group_id=str(request.data.get("group"))
                if request.data.get("group")
                else None,
                period=request.data.get("period"),
                state=request.data.get("state"),
            )
            data = update_use_case.execute(command)
        except EnrollmentNotFoundError:
            return Response({"error": "Enrollment not found"}, status=404)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        return Response(data)
    
    def patch(self, request, pk):
        update_use_case = build_update_enrollment_use_case()

        try:
            command = UpdateEnrollmentCommand(
                enrollment_id=str(pk),
                student_id=str(request.data.get("student"))
                if request.data.get("student")
                else None,
                group_id=str(request.data.get("group"))
                if request.data.get("group")
                else None,
                period=request.data.get("period"),
                state=request.data.get("state"),
            )
            data = update_use_case.execute(command)
        except EnrollmentNotFoundError:
            return Response({"error": "Enrollment not found"}, status=404)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        return Response(data)
    
    def delete(self, request, pk):
        delete_use_case = build_delete_enrollment_use_case()
        try:
            delete_use_case.execute(str(pk))
        except EnrollmentNotFoundError:
            return Response({"error": "Enrollment not found"}, status=404)
        return Response(status=204)


# ClassRoom ViewSet
class ClassRoomViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        staff = self.request.user
        if pk:
            if not can_access_classroom(staff, pk):
                return Response(
                    {"detail": "You do not have access to this classroom."},
                    status=403,
                )
            try:
                classroom = ClassRoom.objects.get(pk=pk)
            except ClassRoom.DoesNotExist:
                return Response({"error": "ClassRoom not found"}, status=404)
            serializer = ClassRoomSerializer(classroom)
            return Response(serializer.data)
        else:
            if is_admin_user(staff):
                classrooms = ClassRoom.objects.all()
            elif is_teacher_user(staff):
                classrooms = ClassRoom.objects.filter(staff=staff)
            else:
                return Response(
                    {"detail": "You do not have permission to access this resource."},
                    status=403,
                )

            serializer = ClassRoomSerializer(classrooms, many=True)
            return Response(serializer.data)

    def post(self, request):
        if not is_admin_user(request.user):
            return Response({"detail": "Only administrators can create classrooms."}, status=403)
        try:
            group = Group.objects.get(pk=request.data.get("group_id"))
            staff = Staff.objects.get(pk=request.data.get("staff_id"))
        except (Group.DoesNotExist, Staff.DoesNotExist, ValueError):
            return Response({"error": "Group or staff not found"}, status=404)
        data = ClassRoom(
            group=group,
            staff=staff,
        )

        serializer = ClassRoomSerializer(data, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def put(self, request, pk):
        if not is_admin_user(request.user):
            return Response({"detail": "Only administrators can update classrooms."}, status=403)
        update_use_case = build_update_classroom_use_case()

        try:
            command = UpdateClassRoomCommand(
                classroom_id=str(pk),
                group_id=str(request.data.get("group_id"))
                if request.data.get("group_id")
                else None,
                staff_id=str(request.data.get("staff_id"))
                if request.data.get("staff_id")
                else None,
            )
            data = update_use_case.execute(command)
        except ClassRoomNotFoundError:
            return Response({"error": "ClassRoom not found"}, status=404)
        except ClassRoomHistoryConflictError as exc:
            return Response({"detail": str(exc)}, status=409)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        return Response(data)

    def delete(self, request, pk):
        if not is_admin_user(request.user):
            return Response({"detail": "Only administrators can delete classrooms."}, status=403)
        delete_use_case = build_delete_classroom_use_case()

        try:
            delete_use_case.execute(str(pk))
        except ClassRoomNotFoundError:
            return Response({"error": "ClassRoom not found"}, status=404)
        except ProtectedError:
            return Response({"detail": HISTORY_PROTECTED_DETAIL}, status=409)
        return Response(status=204)

    def patch(self, request, pk):
        if not is_admin_user(request.user):
            return Response({"detail": "Only administrators can update classrooms."}, status=403)
        update_use_case = build_update_classroom_use_case()

        try:
            command = UpdateClassRoomCommand(
                classroom_id=str(pk),
                group_id=str(request.data.get("group_id"))
                if request.data.get("group_id")
                else None,
                staff_id=str(request.data.get("staff_id"))
                if request.data.get("staff_id")
                else None,
            )
            data = update_use_case.execute(command)
        except ClassRoomNotFoundError:
            return Response({"error": "ClassRoom not found"}, status=404)
        except ClassRoomHistoryConflictError as exc:
            return Response({"detail": str(exc)}, status=409)
        except ValueError:
            return Response({"error": "Invalid request payload"}, status=400)
        return Response(data)


class PromotionView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = PromotionInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        data = serializer.validated_data
        target_group_data = data.get('target_group')

        command = PromoteStudentsCommand(
            source_classroom_id=str(data['source_classroom_id']),
            period=data['period'],
            students=[
                StudentActionItem(student_id=str(s['student_id']), action=s['action'])
                for s in data['students']
            ],
            target_group=TargetGroupData(
                school_grade_id=str(target_group_data['school_grade_id']),
                letter=target_group_data['letter'],
            ) if target_group_data else None,
        )

        use_case = build_execute_promotion_use_case()
        try:
            result = use_case.execute(command)
        except PromotionError as e:
            return Response(
                {"detail": f"No se pudo completar la promoción. Todos los cambios fueron revertidos. Razón: {e}"},
                status=400,
            )
        except Exception:
            return Response(
                {
                    "detail": (
                        "No se pudo completar la promoción. Todos los cambios fueron "
                        "revertidos debido a un error interno."
                    )
                },
                status=500,
            )

        return Response(PromotionOutputSerializer(result).data, status=200)
