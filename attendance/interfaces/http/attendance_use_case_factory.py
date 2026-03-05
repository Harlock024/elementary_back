from attendance.application.use_cases.attendance_use_cases import (
    CreateAttendanceUseCase,
    ListAttendanceUseCase,
)
from attendance.infrastructure.repositories.django_attendance_repository import (
    DjangoAttendanceRepository,
)


def build_list_attendance_use_case() -> ListAttendanceUseCase:
    return ListAttendanceUseCase(repository=DjangoAttendanceRepository())


def build_create_attendance_use_case() -> CreateAttendanceUseCase:
    return CreateAttendanceUseCase(repository=DjangoAttendanceRepository())
