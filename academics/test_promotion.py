from datetime import date

from django.test import TestCase

from academics.application.dto.academics_dto import (
    PromoteStudentsCommand,
    StudentActionItem,
    TargetGroupData,
)
from academics.application.use_cases.execute_promotion import ExecutePromotionUseCase
from academics.domain.exceptions.academics_exceptions import PromotionError
from academics.models import ClassRoom, Enrollment, Group, SchoolGrade, Subject
from assignments.models import Assignment
from attendance.models import Attendance, CatalogTypeAtendance
from grades.models import GradingCriteria, StudentGrade
from staff.models import Staff
from students.models import Student


class ExecutePromotionHistoryTests(TestCase):
    def setUp(self):
        self.teacher = Staff.objects.create_user(
            username="history-teacher",
            password="pass1234",
            role="Teacher",
        )
        self.source_grade = SchoolGrade.objects.create(name="5to")
        self.target_grade = SchoolGrade.objects.create(name="6to")
        self.source_group = Group.objects.create(
            school_grade=self.source_grade,
            letter="A",
        )
        self.source_classroom = ClassRoom.objects.create(
            group=self.source_group,
            staff=self.teacher,
        )

    def _create_student(self, suffix: str) -> Student:
        return Student.objects.create(
            first_name=f"Alumno {suffix}",
            last_name="Historial",
            curp=f"HISTORIAL{suffix:0>9}"[:18],
            tutor_name="Tutor",
            tutor_phone="5551234567",
            tutor_relationship="Madre",
            enrollment_number=f"HIST-{suffix}",
            date_of_birth="2014-01-01",
            gender="F",
            state="activo",
        )

    def _promotion_command(self, *students: Student) -> PromoteStudentsCommand:
        return PromoteStudentsCommand(
            source_classroom_id=str(self.source_classroom.id),
            period="2026-2027",
            students=[
                StudentActionItem(student_id=str(student.id), action="promote")
                for student in students
            ],
            target_group=TargetGroupData(
                school_grade_id=str(self.target_grade.id),
                letter="A",
            ),
        )

    def test_promotion_preserves_source_history_and_related_academic_data(self):
        student = self._create_student("1")
        historical_enrollment = Enrollment.objects.create(
            student=student,
            group=self.source_group,
            period="2025-2026",
            state="activo",
        )
        subject = Subject.objects.create(
            name="Matemáticas",
            school_grade=self.source_grade,
        )
        attendance_status = CatalogTypeAtendance.objects.create(
            code="P",
            description="Presente",
        )
        attendance = Attendance.objects.create(
            student=student,
            state_code=attendance_status,
            class_room=self.source_classroom,
            date=date(2026, 6, 1),
        )
        criteria = GradingCriteria.objects.create(
            name="Tareas",
            class_room=self.source_classroom,
            percentage="100.00",
        )
        assignment = Assignment.objects.create(
            class_room=self.source_classroom,
            subject=subject,
            grading_criteria=criteria,
            title="Evaluación final",
            due_date=date(2026, 6, 2),
            max_score="10.00",
        )
        student_grade = StudentGrade.objects.create(
            student=student,
            class_room=self.source_classroom,
            subject=subject,
            assignment=assignment,
            score="9.00",
            date=date(2026, 6, 2),
        )

        result = ExecutePromotionUseCase().execute(self._promotion_command(student))

        self.assertEqual(result["promoted"], 1)
        historical_enrollment.refresh_from_db()
        self.assertEqual(historical_enrollment.state, "inactivo")
        self.assertTrue(Group.objects.filter(pk=self.source_group.pk).exists())
        self.assertTrue(ClassRoom.objects.filter(pk=self.source_classroom.pk).exists())
        self.assertTrue(Enrollment.objects.filter(pk=historical_enrollment.pk).exists())
        self.assertTrue(Attendance.objects.filter(pk=attendance.pk).exists())
        self.assertTrue(GradingCriteria.objects.filter(pk=criteria.pk).exists())
        self.assertTrue(Assignment.objects.filter(pk=assignment.pk).exists())
        self.assertTrue(StudentGrade.objects.filter(pk=student_grade.pk).exists())
        self.assertTrue(
            Enrollment.objects.filter(
                student=student,
                group_id=result["target_group_id"],
                period="2026-2027",
                state="activo",
            ).exists()
        )

    def test_promotion_rolls_back_every_change_when_an_enrollment_conflicts(self):
        first_student = self._create_student("2")
        second_student = self._create_student("3")
        first_source_enrollment = Enrollment.objects.create(
            student=first_student,
            group=self.source_group,
            period="2025-2026",
            state="activo",
        )
        second_source_enrollment = Enrollment.objects.create(
            student=second_student,
            group=self.source_group,
            period="2025-2026",
            state="activo",
        )
        target_group = Group.objects.create(
            school_grade=self.target_grade,
            letter="A",
        )
        existing_target_enrollment = Enrollment.objects.create(
            student=second_student,
            group=target_group,
            period="2026-2027",
            state="inactivo",
        )

        with self.assertRaises(PromotionError) as error:
            ExecutePromotionUseCase().execute(
                self._promotion_command(first_student, second_student)
            )

        self.assertIn("entra en conflicto", str(error.exception))
        self.assertNotIn("enrollments_student_id", str(error.exception))

        first_source_enrollment.refresh_from_db()
        second_source_enrollment.refresh_from_db()
        existing_target_enrollment.refresh_from_db()
        self.assertEqual(first_source_enrollment.state, "activo")
        self.assertEqual(second_source_enrollment.state, "activo")
        self.assertEqual(existing_target_enrollment.state, "inactivo")
        self.assertFalse(
            Enrollment.objects.filter(
                student=first_student,
                group=target_group,
                period="2026-2027",
            ).exists()
        )
        self.assertFalse(ClassRoom.objects.filter(group=target_group).exists())
        self.assertTrue(Group.objects.filter(pk=self.source_group.pk).exists())
        self.assertTrue(ClassRoom.objects.filter(pk=self.source_classroom.pk).exists())
