from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal

from django.db import close_old_connections
from django.test import TestCase, TransactionTestCase
from rest_framework.test import APIClient

from academics.application.dto.academics_dto import (
    PromoteStudentsCommand,
    StudentActionItem,
    TargetGroupData,
)
from academics.application.use_cases.execute_promotion import ExecutePromotionUseCase
from academics.models import AcademicPeriod, ClassRoom, Enrollment, Group, SchoolGrade
from elementary_back.permissions import can_access_student_classrooms
from grades.application.dto.grading_criteria_dto import CreateGradingCriteriaCommand
from grades.infrastructure.repositories.django_grading_criteria_repository import DjangoGradingCriteriaRepository
from staff.models import Staff
from students.models import Student


def create_student(suffix="1"):
    return Student.objects.create(
        first_name="Alumno",
        last_name="Temporal",
        curp=f"TEMPORAL{suffix:0>10}"[:18],
        tutor_name="Tutor",
        tutor_phone="5551234567",
        tutor_relationship="Madre",
        enrollment_number=f"TEMP-{suffix}",
        date_of_birth="2015-01-01",
        gender="F",
        state="activo",
    )


class AcademicPeriodTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = Staff.objects.create_user(
            username="period-admin", password="pass1234", role="Admin"
        )
        self.teacher = Staff.objects.create_user(
            username="period-teacher", password="pass1234", role="Teacher"
        )
        self.other_teacher = Staff.objects.create_user(
            username="period-other", password="pass1234", role="Teacher"
        )
        self.active = AcademicPeriod.objects.get(status="active")
        self.active.name = "2025-2026"
        self.active.start_date = date(2025, 8, 1)
        self.active.end_date = date(2026, 7, 31)
        self.active.save()
        self.next_period = AcademicPeriod.objects.create(
            name="2026-2027",
            start_date=date(2026, 8, 1),
            end_date=date(2027, 7, 31),
            status="draft",
        )
        self.grade = SchoolGrade.objects.create(name="5to")
        self.next_grade = SchoolGrade.objects.create(name="6to")
        self.group = Group.objects.create(school_grade=self.grade, letter="A")
        self.classroom = ClassRoom.objects.create(
            staff=self.teacher,
            group=self.group,
            academic_period=self.active,
        )

    def test_teacher_only_lists_assigned_periods(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.get("/api/academics/periods/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.data], [str(self.active.id)])

    def test_teacher_cannot_create_period(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.post(
            "/api/academics/periods/",
            {"name": "2027-2028", "start_date": "2027-08-01", "end_date": "2028-07-31"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_second_active_period_is_rejected(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(
            f"/api/academics/periods/{self.next_period.id}/",
            {"status": "active"},
            format="json",
        )
        self.assertEqual(response.status_code, 409)

    def test_active_period_with_enrollments_cannot_be_closed(self):
        student = create_student("close")
        Enrollment.objects.create(
            student=student,
            group=self.group,
            period=self.active.name,
            academic_period=self.active,
            state="activo",
        )
        self.client.force_authenticate(self.admin)
        response = self.client.patch(
            f"/api/academics/periods/{self.active.id}/",
            {"status": "closed"},
            format="json",
        )
        self.assertEqual(response.status_code, 409)

    def test_same_group_in_another_period_does_not_grant_teacher_access(self):
        student = create_student("scope")
        Enrollment.objects.create(
            student=student,
            group=self.group,
            period=self.next_period.name,
            academic_period=self.next_period,
            state="activo",
        )
        self.assertFalse(can_access_student_classrooms(self.teacher, student.id))

    def test_closed_classroom_is_read_only(self):
        self.active.status = "closed"
        self.active.save(update_fields=["status"])
        self.client.force_authenticate(self.teacher)
        response = self.client.post(
            f"/api/assignments/classroom/{self.classroom.id}/",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, 409)

    def test_promotion_is_idempotent(self):
        student = create_student("promotion")
        Enrollment.objects.create(
            student=student,
            group=self.group,
            period=self.active.name,
            academic_period=self.active,
            state="activo",
        )
        command = PromoteStudentsCommand(
            source_classroom_id=str(self.classroom.id),
            target_period_id=str(self.next_period.id),
            students=[StudentActionItem(student_id=str(student.id), action="promote")],
            target_group=TargetGroupData(
                school_grade_id=str(self.next_grade.id),
                letter="A",
            ),
        )
        first = ExecutePromotionUseCase().execute(command)
        second = ExecutePromotionUseCase().execute(command)
        self.assertEqual(first["promoted"], 1)
        self.assertEqual(second["promoted"], 1)
        self.assertEqual(
            Enrollment.objects.filter(
                student=student,
                academic_period=self.next_period,
                state="activo",
            ).count(),
            1,
        )

    def test_graduation_does_not_require_a_target_period(self):
        student = create_student("graduate")
        enrollment = Enrollment.objects.create(
            student=student,
            group=self.group,
            period=self.active.name,
            academic_period=self.active,
            state="activo",
        )
        result = ExecutePromotionUseCase().execute(
            PromoteStudentsCommand(
                source_classroom_id=str(self.classroom.id),
                students=[
                    StudentActionItem(student_id=str(student.id), action="graduate")
                ],
            )
        )
        enrollment.refresh_from_db()
        student.refresh_from_db()
        self.assertEqual(result["graduated"], 1)
        self.assertEqual(enrollment.state, "inactivo")
        self.assertEqual(student.state, "inactivo")


class CriteriaConcurrencyTests(TransactionTestCase):
    def setUp(self):
        period = AcademicPeriod.objects.filter(status="active").first()
        if period is None:
            period = AcademicPeriod.objects.create(
                name="2025-2026",
                start_date=date(2025, 8, 1),
                end_date=date(2026, 7, 31),
                status="active",
            )
        teacher = Staff.objects.create_user(
            username="criteria-concurrency", password="pass1234", role="Teacher"
        )
        grade = SchoolGrade.objects.create(name="4to")
        group = Group.objects.create(school_grade=grade, letter="C")
        self.classroom = ClassRoom.objects.create(
            staff=teacher,
            group=group,
            academic_period=period,
        )

    def _create_criteria(self, name):
        close_old_connections()
        try:
            DjangoGradingCriteriaRepository().create_grading_criteria(
                CreateGradingCriteriaCommand(
                    name=name,
                    class_room_id=str(self.classroom.id),
                    percentage=Decimal("60"),
                )
            )
            return "created"
        except ValueError:
            return "rejected"
        finally:
            close_old_connections()

    def test_parallel_percentages_cannot_exceed_one_hundred(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            outcomes = list(executor.map(self._create_criteria, ["A", "B"]))
        self.assertCountEqual(outcomes, ["created", "rejected"])
