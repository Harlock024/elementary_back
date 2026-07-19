from django.db import IntegrityError, transaction

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
                enrollments__academic_period_id=classroom.academic_period_id,
                enrollments__state__in=('activo', 'active'),
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
        try:
            with transaction.atomic():
                class_room = ClassRoom.objects.select_for_update().select_related(
                    "academic_period"
                ).filter(id=command.class_id).first()
                if class_room is None:
                    raise ClassRoomNotFoundError("Class room does not exist.")
                if class_room.academic_period.status == "closed":
                    raise ValueError("The academic period is closed")
                if not class_room.academic_period.start_date <= command.attendance_date <= class_room.academic_period.end_date:
                    raise ValueError("Attendance date is outside the academic period")
                student = Student.objects.select_for_update().filter(id=command.student_id).first()
                if student is None:
                    raise StudentNotFoundForAttendanceError("Student does not exist.")
                if not student.enrollments.filter(
                    group_id=class_room.group_id,
                    academic_period_id=class_room.academic_period_id,
                    state__in=("activo", "active"),
                ).exists():
                    raise StudentNotFoundForAttendanceError("Student is not enrolled in this classroom period.")
                state_code = CatalogTypeAtendance.objects.filter(id=command.state_code_id).first()
                if state_code is None:
                    raise StateCodeNotFoundError("State code does not exist.")
                attendance = Attendance.objects.create(
                    class_room=class_room,
                    student=student,
                    date=command.attendance_date,
                    state_code=state_code,
                )
        except IntegrityError:
            raise AttendanceAlreadyExistsError(
                "Attendance for this student in this class already exists."
            )

        serializer = AttendanceCreateUpdateSerializer(attendance)
        return serializer.data

    def update_attendance(self, command: UpdateAttendanceCommand) -> dict:
        attendance = Attendance.objects.select_related("class_room__academic_period").filter(pk=command.attendance_id).first()
        if attendance is None:
            raise AttendanceNotFoundError("Attendance record not found")
        if attendance.class_room.academic_period.status == "closed":
            raise ValueError("The academic period is closed")

        if command.state_code_id is not None:
            state_code = CatalogTypeAtendance.objects.filter(id=command.state_code_id).first()
            if state_code is None:
                raise StateCodeNotFoundError("State code does not exist.")
            attendance.state_code = state_code

        attendance.save()
        serializer = AttendanceCreateUpdateSerializer(attendance)
        return serializer.data
