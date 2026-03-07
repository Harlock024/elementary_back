from attendance.application.use_cases.attendance_use_cases import (
    CreateAttendanceUseCase,
    ListAttendanceUseCase,
)
from attendance.application.use_cases.update_attendance import UpdateAttendanceUseCase
from attendance.infrastructure.repositories.django_attendance_repository import (
    DjangoAttendanceRepository,
)


def build_list_attendance_use_case() -> ListAttendanceUseCase:
    return ListAttendanceUseCase(repository=DjangoAttendanceRepository())


def build_create_attendance_use_case() -> CreateAttendanceUseCase:
    return CreateAttendanceUseCase(repository=DjangoAttendanceRepository())


def build_update_attendance_use_case() -> UpdateAttendanceUseCase:
    return UpdateAttendanceUseCase(repository=DjangoAttendanceRepository())
