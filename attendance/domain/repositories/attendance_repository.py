from typing import Protocol

from attendance.application.dto.attendance_dto import CreateAttendanceCommand


class AttendanceRepository(Protocol):
    def list_attendance(
        self,
        class_id: str | None = None,
        attendance_date: str | None = None,
        student_id: str | None = None,
    ) -> list[dict]:
        ...

    def create_attendance(self, command: CreateAttendanceCommand) -> dict:
        ...
