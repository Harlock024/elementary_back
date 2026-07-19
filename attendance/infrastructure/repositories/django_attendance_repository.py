from attendance.application.dto.attendance_dto import CreateAttendanceCommand, UpdateAttendanceCommand
from attendance.domain.exceptions.attendance_exceptions import (
    AttendanceAlreadyExistsError,
    AttendanceNotFoundError,
    ClassRoomNotFoundError,
    StateCodeNotFoundError,
    StudentNotFoundForAttendanceError,
)
from attendance.models import Attendance, CatalogTypeAtendance
from attendance.serializer import AttendanceCreateUpdateSerializer, AttendanceSerializer
from academics.models import ClassRoom
from students.models import Student
from students.base_serializer import StudentSerializerNameOnly


class DjangoAttendanceRepository:
    def list_attendance(
        self,
        class_id: str | None = None,
        attendance_date: str | None = None,
        student_id: str | None = None,
    ) -> list[dict]:

        if class_id and attendance_date:
            classroom = ClassRoom.objects.select_related('group').filter(id=class_id).first()
            if classroom is None:
                return []
            students = Student.objects.filter(
                enrollments__group=classroom.group,
                enrollments__state='activo',
            ).distinct()
            result = []
            for student in students:
                attendance = Attendance.objects.filter(
                    student=student,
                    date=attendance_date,
                    class_room=classroom,
                ).first()
                result.append({
                    'student': StudentSerializerNameOnly(student).data,
                    'attendance': AttendanceSerializer(attendance).data if attendance else None,
                })
            return result

        attendance = Attendance.objects.all()
        if class_id:
            attendance = attendance.filter(class_room_id=class_id)
        elif student_id and attendance_date:
            attendance = attendance.filter(student_id=student_id, date=attendance_date)

        return AttendanceSerializer(attendance, many=True).data

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
            class_room=class_room,
            student=student,
            date=command.attendance_date,
            state_code=state_code,
        )
        try:
            attendance.save()
        except Exception:
            raise AttendanceAlreadyExistsError(
                "Attendance for this student in this class already exists."
            )

        serializer = AttendanceCreateUpdateSerializer(attendance)
        return serializer.data

    def update_attendance(self, command: UpdateAttendanceCommand) -> dict:
        attendance = Attendance.objects.filter(pk=command.attendance_id).first()
        if attendance is None:
            raise AttendanceNotFoundError("Attendance record not found")

        if command.state_code_id is not None:
            state_code = CatalogTypeAtendance.objects.filter(id=command.state_code_id).first()
            if state_code is None:
                raise StateCodeNotFoundError("State code does not exist.")
            attendance.state_code = state_code

        attendance.save()
        serializer = AttendanceCreateUpdateSerializer(attendance)
        return serializer.data
