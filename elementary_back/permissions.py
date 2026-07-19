"""Reusable role and classroom authorization helpers for the API."""

from collections.abc import Iterable
from typing import Any

from django.core.exceptions import ValidationError
from django.db.models import F
from rest_framework.exceptions import APIException
from rest_framework.exceptions import PermissionDenied, ValidationError as APIValidationError
from rest_framework.permissions import BasePermission


ADMIN_ROLES = frozenset({"Admin", "Superuser", "Principal"})


class AcademicPeriodClosed(APIException):
    status_code = 409
    default_detail = "The academic period is closed and is read-only."
    default_code = "academic_period_closed"


def _is_authenticated(user: Any) -> bool:
    return bool(user and getattr(user, "is_authenticated", False))


def is_admin_user(user: Any) -> bool:
    """Return whether ``user`` has an administrative role."""
    return _is_authenticated(user) and (
        bool(getattr(user, "is_superuser", False))
        or getattr(user, "role", None) in ADMIN_ROLES
    )


def is_teacher_user(user: Any) -> bool:
    """Return whether ``user`` is an authenticated teacher."""
    return _is_authenticated(user) and getattr(user, "role", None) == "Teacher"


def can_access_classroom(user: Any, classroom_id: Any) -> bool:
    """Allow admins or the teacher assigned to the given classroom."""
    if is_admin_user(user):
        return True
    if not is_teacher_user(user) or not classroom_id:
        return False

    from academics.models import ClassRoom

    try:
        return ClassRoom.objects.filter(pk=classroom_id, staff_id=user.pk).exists()
    except (TypeError, ValueError, ValidationError):
        return False


def can_access_classrooms(user: Any, classroom_ids: Iterable[Any]) -> bool:
    """Return whether every classroom in ``classroom_ids`` is accessible."""
    if is_admin_user(user):
        return True

    if not is_teacher_user(user):
        return False

    ids = {classroom_id for classroom_id in classroom_ids if classroom_id}
    if not ids:
        return False

    from academics.models import ClassRoom

    try:
        accessible_count = ClassRoom.objects.filter(
            pk__in=ids,
            staff_id=user.pk,
        ).count()
    except (TypeError, ValueError, ValidationError):
        return False
    return accessible_count == len(ids)


def can_access_student_classrooms(user: Any, student_id: Any) -> bool:
    """Allow access when a student is actively enrolled in an assigned classroom."""
    if is_admin_user(user):
        return True
    if not is_teacher_user(user) or not student_id:
        return False

    from academics.models import ClassRoom

    try:
        return ClassRoom.objects.filter(
            staff_id=user.pk,
            group__enrollments__student_id=student_id,
            group__enrollments__state__in=("activo", "active"),
            group__enrollments__academic_period_id=F("academic_period_id"),
        ).exists()
    except (TypeError, ValueError, ValidationError):
        return False


def student_is_enrolled_in_classroom(student_id: Any, classroom_id: Any) -> bool:
    """Return whether the student has an active enrollment in the classroom group."""
    if not student_id or not classroom_id:
        return False

    from academics.models import Enrollment

    try:
        return Enrollment.objects.filter(
            student_id=student_id,
            group__classes__id=classroom_id,
            academic_period_id=F("group__classes__academic_period_id"),
            state__in=("activo", "active"),
        ).exists()
    except (TypeError, ValueError, ValidationError):
        return False


def classroom_ids_for_active_student(student_id: Any) -> list[Any]:
    """Return classrooms linked to the student's active enrollments."""
    if not student_id:
        return []

    from academics.models import ClassRoom

    try:
        return list(
            ClassRoom.objects.filter(
                group__enrollments__student_id=student_id,
                group__enrollments__state__in=("activo", "active"),
                group__enrollments__academic_period_id=F("academic_period_id"),
            )
            .values_list("id", flat=True)
            .distinct()
        )
    except (TypeError, ValueError, ValidationError):
        return []


def classroom_id_for_assignment(assignment_id: Any) -> Any | None:
    from assignments.models import Assignment

    try:
        return Assignment.objects.filter(pk=assignment_id).values_list(
            "class_room_id", flat=True
        ).first()
    except (TypeError, ValueError, ValidationError):
        return None


def classroom_id_for_attendance(attendance_id: Any) -> Any | None:
    from attendance.models import Attendance

    try:
        return Attendance.objects.filter(pk=attendance_id).values_list(
            "class_room_id", flat=True
        ).first()
    except (TypeError, ValueError, ValidationError):
        return None


def classroom_id_for_grade(grade_id: Any) -> Any | None:
    from grades.models import StudentGrade

    try:
        return StudentGrade.objects.filter(pk=grade_id).values_list(
            "class_room_id", flat=True
        ).first()
    except (TypeError, ValueError, ValidationError):
        return None


def classroom_id_for_grading_criteria(criteria_id: Any) -> Any | None:
    from grades.models import GradingCriteria

    try:
        return GradingCriteria.objects.filter(pk=criteria_id).values_list(
            "class_room_id", flat=True
        ).first()
    except (TypeError, ValueError, ValidationError):
        return None


def require_admin(user: Any) -> None:
    if not is_admin_user(user):
        raise PermissionDenied("Administrator access is required.")


def require_classroom_access(user: Any, classroom_id: Any) -> None:
    if not can_access_classroom(user, classroom_id):
        raise PermissionDenied("You do not have access to this classroom.")


def require_open_classroom(classroom_id: Any) -> None:
    from academics.models import AcademicPeriod, ClassRoom

    if ClassRoom.objects.filter(
        pk=classroom_id,
        academic_period__status=AcademicPeriod.Status.CLOSED,
    ).exists():
        raise AcademicPeriodClosed()


def require_student_classroom_access(
    user: Any, student_id: Any, classroom_id: Any
) -> None:
    require_classroom_access(user, classroom_id)
    if student_is_enrolled_in_classroom(student_id, classroom_id):
        return

    # Preserve object-level authorization semantics before reporting a bad
    # cross-classroom relationship. A teacher must not learn or link a student
    # whose active classroom belongs to somebody else. If every related
    # classroom is accessible (or the caller is an admin), the relationship is
    # simply invalid for the selected classroom and is reported as a safe 400.
    for related_classroom_id in classroom_ids_for_active_student(student_id):
        require_classroom_access(user, related_classroom_id)

    raise APIValidationError("The student is not actively enrolled in this classroom.")


class IsAdminRole(BasePermission):
    message = "Administrator access is required."

    def has_permission(self, request, view):
        return is_admin_user(request.user)


class IsAdminOrTeacher(BasePermission):
    message = "A school staff role is required."

    def has_permission(self, request, view):
        return is_admin_user(request.user) or is_teacher_user(request.user)
