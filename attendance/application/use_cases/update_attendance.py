from attendance.application.dto.attendance_dto import UpdateAttendanceCommand
from attendance.domain.repositories.attendance_repository import AttendanceRepository


class UpdateAttendanceUseCase:
    def __init__(self, repository: AttendanceRepository):
        self.repository = repository

    def execute(self, command: UpdateAttendanceCommand) -> dict:
        return self.repository.update_attendance(command)
