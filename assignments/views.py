from datetime import datetime

from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from rest_framework.response import Response
from rest_framework.views import APIView

from academics.models import ClassRoom, Subject
from elementary_back.permissions import (
    IsAdminOrTeacher,
    can_access_student_classrooms,
    classroom_id_for_assignment,
    classroom_id_for_grading_criteria,
    is_admin_user,
    require_admin,
    require_classroom_access,
    require_open_classroom,
)
from grades.models import GradingCriteria

from assignments.application.dtos.assignments_dto import (
    CreateAssignmentCommand,
    UpdateAssignmentCommand,
)
from assignments.domain.exceptions.assignments_exception import (
    AssignmentsAlreadyExistsError,
    AssignmentsNotFoundError,
    ClassRoomNotFoundError,
    StudentNotFoundForAssignmentsError,
)
from assignments.interfaces.http.assignment_use_case_factory import (
    build_create_assignment_use_case,
    build_delete_assignment_use_case,
    build_list_assignments_use_case,
    build_update_assignment_use_case,
)


HISTORY_PROTECTED_DETAIL = (
    "No se puede eliminar esta tarea porque forma parte del historial académico."
)


def _assignment_relation_error(class_id, subject_id, criteria_id):
    try:
        classroom = ClassRoom.objects.select_related("group").filter(pk=class_id).first()
        subject = Subject.objects.filter(pk=subject_id).first()
        criteria = GradingCriteria.objects.filter(pk=criteria_id).first()
    except (TypeError, ValueError, ValidationError):
        return "Classroom, subject, or grading criteria not found."
    if classroom is None or subject is None or criteria is None:
        return "Classroom, subject, or grading criteria not found."
    if criteria.class_room_id != classroom.id:
        return "Grading criteria must belong to the assignment classroom."
    if subject.school_grade_id != classroom.group.school_grade_id:
        return "Subject must belong to the classroom school grade."
    return None


class AssignmentView(APIView):
    permission_classes = [IsAdminOrTeacher]

    def get(self, request, class_id=None, student_id=None, date=None):
        due_date = None
        authorized_classroom_ids = None
        if date:
            try:
                due_date = datetime.fromisoformat(date).date()
            except ValueError:
                return Response({"error": "Invalid date format"}, status=400)

        if class_id:
            require_classroom_access(request.user, class_id)
        elif student_id:
            if not is_admin_user(request.user):
                if not can_access_student_classrooms(request.user, student_id):
                    require_admin(request.user)
                authorized_classroom_ids = [
                    str(classroom_id)
                    for classroom_id in ClassRoom.objects.filter(
                        staff=request.user,
                        group__enrollments__student_id=student_id,
                        group__enrollments__state__in=("activo", "active"),
                    ).values_list("id", flat=True).distinct()
                ]
        else:
            require_admin(request.user)

        use_case = build_list_assignments_use_case()
        assignment_data = use_case.execute(
            class_id=str(class_id) if class_id else None,
            student_id=str(student_id) if student_id else None,
            due_date=due_date,
            classroom_ids=authorized_classroom_ids,
        )
        return Response(assignment_data, status=200)

    def post(self, request, class_id=None):
        if not class_id:
            require_admin(request.user)
            return Response({"error": "Class ID is required"}, status=400)

        require_classroom_access(request.user, class_id)
        require_open_classroom(class_id)

        subject_id = request.data.get("subject_id")
        grading_criteria_id = request.data.get("grading_criteria_id")
        title = request.data.get("title")
        description = request.data.get("description")
        due_date = request.data.get("due_date")
        max_score = request.data.get("max_score")

        criteria_classroom_id = classroom_id_for_grading_criteria(
            grading_criteria_id
        )
        if criteria_classroom_id is not None:
            require_classroom_access(request.user, criteria_classroom_id)

        if (
            not subject_id
            or not grading_criteria_id
            or not title
            or not due_date
            or not max_score
        ):
            return Response(
                {
                    "error": "subject_id  , grading_criteria_id, title, due_date and max_score are required"
                },
                status=400,
            )

        relation_error = _assignment_relation_error(
            class_id,
            subject_id,
            grading_criteria_id,
        )
        if relation_error:
            return Response({"error": relation_error}, status=400)

        use_case = build_create_assignment_use_case()
        try:
            command = CreateAssignmentCommand(
                class_id=str(class_id),
                subject_id=str(subject_id),
                grading_criteria_id=str(grading_criteria_id),
                title=title,
                description=description,
                due_date=datetime.fromisoformat(due_date),
                max_score=int(max_score),
            )
            data = use_case.execute(command)
            return Response(data, status=201)
        except ValueError:
            return Response({"error": "Invalid date format for due_date"}, status=400)
        except AssignmentsAlreadyExistsError as exc:
            return Response({"error": str(exc)}, status=400)
        except StudentNotFoundForAssignmentsError as exc:
            return Response({"error": str(exc)}, status=400)
        except ClassRoomNotFoundError as exc:
            return Response({"error": str(exc)}, status=400)

    def delete(self, request, id=None):
        if not id:
            return Response({"error": "Assignment ID is required"}, status=400)

        classroom_id = classroom_id_for_assignment(id)
        if classroom_id is None:
            if not is_admin_user(request.user):
                require_admin(request.user)
        else:
            require_classroom_access(request.user, classroom_id)
            require_open_classroom(classroom_id)

        try:
            build_delete_assignment_use_case().execute(str(id))
        except AssignmentsNotFoundError:
            return Response({"error": "Assignment not found"}, status=404)
        except ProtectedError:
            return Response({"detail": HISTORY_PROTECTED_DETAIL}, status=409)
        return Response(status=204)

    def patch(self, request, id=None):
        if not id:
            return Response({"error": "Assignment ID is required"}, status=400)

        classroom_id = classroom_id_for_assignment(id)
        if classroom_id is None:
            if not is_admin_user(request.user):
                require_admin(request.user)
        else:
            require_classroom_access(request.user, classroom_id)
            require_open_classroom(classroom_id)

        subject_id = request.data.get("subject_id")
        grading_criteria_id = request.data.get("grading_criteria_id")
        title = request.data.get("title")
        description = request.data.get("description")
        due_date = request.data.get("due_date")
        max_score = request.data.get("max_score")

        if subject_id or grading_criteria_id:
            from assignments.models import Assignment

            assignment = Assignment.objects.filter(pk=id).first()
            if assignment is not None:
                if grading_criteria_id:
                    criteria_classroom_id = classroom_id_for_grading_criteria(
                        grading_criteria_id
                    )
                    if criteria_classroom_id is not None:
                        require_classroom_access(
                            request.user,
                            criteria_classroom_id,
                        )
                relation_error = _assignment_relation_error(
                    assignment.class_room_id,
                    subject_id or assignment.subject_id,
                    grading_criteria_id or assignment.grading_criteria_id,
                )
                if relation_error:
                    return Response({"error": relation_error}, status=400)

        update_use_case = build_update_assignment_use_case()
        try:
            command = UpdateAssignmentCommand(
                assignment_id=str(id),
                subject_id=str(subject_id) if subject_id else None,
                grading_criteria_id=str(grading_criteria_id)
                if grading_criteria_id
                else None,
                title=title if title else None,
                description=description if description else None,
                due_date=datetime.fromisoformat(due_date) if due_date else None,
                max_score=int(max_score) if max_score else None,
            )
            data = update_use_case.execute(command)
            return Response(data, status=200)
        except ValueError:
            return Response({"error": "Invalid date format for due_date"}, status=400)
        except AssignmentsNotFoundError as exc:
            return Response({"error": str(exc)}, status=404)
        except StudentNotFoundForAssignmentsError as exc:
            return Response({"error": str(exc)}, status=400)
        except ClassRoomNotFoundError as exc:
            return Response({"error": str(exc)}, status=400)
