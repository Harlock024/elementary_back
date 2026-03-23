from django.utils import timezone

from attendance.application.dto.attendance_dto import CreateAttendanceCommand, UpdateAttendanceCommand
from attendance.domain.exceptions.attendance_exceptions import (
    AttendanceAlreadyExistsError,
    AttendanceNotFoundError,
    AttendanceVersionConflictError,
    ClassRoomNotFoundError,
    StateCodeNotFoundError,
    StudentNotFoundForAttendanceError,
)
from attendance.models import Attendance, CatalogTypeAtendance
from attendance.serializer import AttendanceCreateUpdateSerializer, AttendanceSerializer
from academics.models import ClassRoom
from students.models import Student


class DjangoAttendanceRepository:
    def list_attendance(
        self,
        class_id: str | None = None,
        attendance_date: str | None = None,
        student_id: str | None = None,
    ) -> list[dict]:
        attendance = Attendance.objects.all()

        if class_id and attendance_date:
            attendance = attendance.filter(class_room_id=class_id, date=attendance_date)
        elif class_id:
            attendance = attendance.filter(class_room_id=class_id)
        elif student_id and attendance_date:
            attendance = attendance.filter(student_id=student_id, date=attendance_date)

        serializer = AttendanceSerializer(attendance, many=True)
        return serializer.data

    def create_attendance(self, command: CreateAttendanceCommand) -> dict:
        existing = Attendance.objects.filter(
            date=command.attendance_date,
            student_id=command.student_id,
        )
        if existing.exists():
            raise AttendanceAlreadyExistsError(
                "Attendance for this student in this class already exists."
            )

        student = Student.objects.filter(id=command.student_id).first()
        if student is None:
            raise StudentNotFoundForAttendanceError("Student does not exist.")

        state_code = CatalogTypeAtendance.objects.filter(id=command.state_code_id).first()
        if state_code is None:
            raise StateCodeNotFoundError("State code does not exist.")

        class_room = ClassRoom.objects.filter(id=command.class_id).first()
        if class_room is None:
            raise ClassRoomNotFoundError("Class room does not exist.")

        attendance = Attendance(
            id=command.id if command.id else None,
            class_room=class_room,
            student=student,
            date=command.attendance_date,
            state_code=state_code,
            syncStatus='pending',
            version=1,
            localUpdatedAt=timezone.now(),
        )
        attendance.save()

        serializer = AttendanceCreateUpdateSerializer(attendance)
        return serializer.data

    def update_attendance(self, command: UpdateAttendanceCommand) -> dict:
        attendance = Attendance.objects.filter(pk=command.attendance_id).first()
        if attendance is None:
            raise AttendanceNotFoundError("Attendance record not found")

        if command.version != attendance.version:
            raise AttendanceVersionConflictError("Version conflict")

        if command.state_code_id is not None:
            state_code = CatalogTypeAtendance.objects.filter(id=command.state_code_id).first()
            if state_code is None:
                raise StateCodeNotFoundError("State code does not exist.")
            attendance.state_code = state_code

        attendance.version += 1
        attendance.syncStatus = 'synced'
        attendance.localUpdatedAt = timezone.now()

        attendance.save()
        serializer = AttendanceCreateUpdateSerializer(attendance)
        return serializer.data
