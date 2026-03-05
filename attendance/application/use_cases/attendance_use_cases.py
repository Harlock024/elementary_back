from attendance.application.dto.attendance_dto import CreateAttendanceCommand
from attendance.domain.entities.attendance_entity import AttendanceEntity
from attendance.domain.repositories.attendance_repository import AttendanceRepository


class ListAttendanceUseCase:
    def __init__(self, repository: AttendanceRepository):
        self.repository = repository

    def execute(
        self,
        class_id: str | None = None,
        attendance_date: str | None = None,
        student_id: str | None = None,
    ) -> list[dict]:
        return self.repository.list_attendance(
            class_id=class_id,
            attendance_date=attendance_date,
            student_id=student_id,
        )


class CreateAttendanceUseCase:
    def __init__(self, repository: AttendanceRepository):
        self.repository = repository

    def execute(self, command: CreateAttendanceCommand) -> dict:
        AttendanceEntity(
            student_id=command.student_id,
            state_code_id=command.state_code_id,
            class_id=command.class_id,
            attendance_date=command.attendance_date,
        )
        return self.repository.create_attendance(command)
