from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from rest_framework.test import APIClient

from academics.models import ClassRoom, Enrollment, Group, SchoolGrade, Subject
from assignments.models import Assignment
from attendance.models import Attendance, CatalogTypeAtendance
from grades.models import GradingCriteria, StudentGrade
from staff.models import Staff
from students.models import Student


class AcademicHistoryProtectionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = Staff.objects.create_user(
            username="history-admin",
            password="SecurePass!2026",
            role="Admin",
        )
        self.teacher = Staff.objects.create_user(
            username="history-owner",
            password="SecurePass!2026",
            role="Teacher",
        )
        self.client.force_authenticate(self.admin)

        self.school_grade = SchoolGrade.objects.create(name="4to-history")
        self.group = Group.objects.create(
            school_grade=self.school_grade,
            letter="A",
        )
        self.classroom = ClassRoom.objects.create(
            group=self.group,
            staff=self.teacher,
        )
        self.subject = Subject.objects.create(
            name="Historia protegida",
            school_grade=self.school_grade,
        )
        self.student = Student.objects.create(
            first_name="Alumno",
            last_name="Protegido",
            curp="HIST260101HDFABC01",
            tutor_name="Tutor",
            tutor_phone="5551234567",
            tutor_relationship="Madre",
            enrollment_number="HISTORY-001",
            date_of_birth="2015-01-01",
            gender="X",
            state="activo",
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            group=self.group,
            period="2025-2026",
            state="activo",
        )
        attendance_status = CatalogTypeAtendance.objects.create(
            code="P",
            description="Presente",
        )
        self.attendance = Attendance.objects.create(
            student=self.student,
            state_code=attendance_status,
            class_room=self.classroom,
            date=date(2026, 6, 1),
        )
        self.criteria = GradingCriteria.objects.create(
            name="Tareas",
            class_room=self.classroom,
            percentage=Decimal("100.00"),
        )
        self.assignment = Assignment.objects.create(
            class_room=self.classroom,
            subject=self.subject,
            grading_criteria=self.criteria,
            title="Trabajo histórico",
            due_date=date(2026, 6, 2),
            max_score=Decimal("10.00"),
        )
        self.grade = StudentGrade.objects.create(
            student=self.student,
            class_room=self.classroom,
            subject=self.subject,
            assignment=self.assignment,
            score=Decimal("9.00"),
            date=date(2026, 6, 2),
        )

    def test_protected_delete_endpoints_return_safe_409_and_keep_history(self):
        protected_urls = (
            f"/api/staff/{self.teacher.id}/",
            f"/api/staff/professors/{self.teacher.id}/delete/",
            f"/api/students/{self.student.id}/",
            f"/api/academics/groups/{self.group.id}/",
            f"/api/academics/classrooms/{self.classroom.id}/",
            f"/api/academics/subjects/{self.subject.id}/",
            f"/api/grades/grading-criteria/{self.criteria.id}/",
            f"/api/assignments/{self.assignment.id}/",
        )

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.delete(url)
                self.assertEqual(response.status_code, 409)
                detail = response.data.get("detail", "")
                self.assertTrue(detail)
                self.assertNotIn("ProtectedError", detail)
                self.assertNotIn("student_grades", detail)

        self.assertTrue(Staff.objects.filter(pk=self.teacher.pk).exists())
        self.assertTrue(Student.objects.filter(pk=self.student.pk).exists())
        self.assertTrue(SchoolGrade.objects.filter(pk=self.school_grade.pk).exists())
        self.assertTrue(Group.objects.filter(pk=self.group.pk).exists())
        self.assertTrue(ClassRoom.objects.filter(pk=self.classroom.pk).exists())
        self.assertTrue(Subject.objects.filter(pk=self.subject.pk).exists())
        self.assertTrue(Enrollment.objects.filter(pk=self.enrollment.pk).exists())
        self.assertTrue(Attendance.objects.filter(pk=self.attendance.pk).exists())
        self.assertTrue(GradingCriteria.objects.filter(pk=self.criteria.pk).exists())
        self.assertTrue(Assignment.objects.filter(pk=self.assignment.pk).exists())
        self.assertTrue(StudentGrade.objects.filter(pk=self.grade.pk).exists())

    def test_school_grade_cannot_cascade_delete_groups_or_subjects(self):
        with self.assertRaises(ProtectedError):
            self.school_grade.delete()

        self.assertTrue(SchoolGrade.objects.filter(pk=self.school_grade.pk).exists())
        self.assertTrue(Group.objects.filter(pk=self.group.pk).exists())
        self.assertTrue(Subject.objects.filter(pk=self.subject.pk).exists())

    def test_delete_enrollment_is_a_soft_delete(self):
        response = self.client.delete(
            f"/api/academics/enrollments/{self.enrollment.id}/"
        )

        self.assertEqual(response.status_code, 204)
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.state, "inactivo")
        self.assertTrue(StudentGrade.objects.filter(pk=self.grade.pk).exists())
        self.assertTrue(Attendance.objects.filter(pk=self.attendance.pk).exists())

    def test_group_and_classroom_natural_keys_are_unique(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Group.objects.create(
                    school_grade=self.school_grade,
                    letter=self.group.letter,
                )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ClassRoom.objects.create(
                    group=self.group,
                    staff=self.admin,
                )

    def test_classroom_with_history_cannot_be_reassigned_to_another_teacher(self):
        response = self.client.patch(
            f"/api/academics/classrooms/{self.classroom.id}/",
            {"staff_id": str(self.admin.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 409)
        self.classroom.refresh_from_db()
        self.assertEqual(self.classroom.staff_id, self.teacher.id)
        self.assertTrue(Attendance.objects.filter(pk=self.attendance.pk).exists())

    def test_classroom_with_history_cannot_be_reassigned_to_another_group(self):
        target_group = Group.objects.create(
            school_grade=self.school_grade,
            letter="B",
        )

        response = self.client.put(
            f"/api/academics/classrooms/{self.classroom.id}/",
            {"group_id": str(target_group.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 409)
        self.classroom.refresh_from_db()
        self.assertEqual(self.classroom.group_id, self.group.id)
        self.assertTrue(StudentGrade.objects.filter(pk=self.grade.pk).exists())

    def test_empty_classroom_can_be_reassigned(self):
        source_group = Group.objects.create(
            school_grade=self.school_grade,
            letter="C",
        )
        target_group = Group.objects.create(
            school_grade=self.school_grade,
            letter="D",
        )
        empty_classroom = ClassRoom.objects.create(
            group=source_group,
            staff=self.teacher,
        )

        response = self.client.patch(
            f"/api/academics/classrooms/{empty_classroom.id}/",
            {
                "group_id": str(target_group.id),
                "staff_id": str(self.admin.id),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        empty_classroom.refresh_from_db()
        self.assertEqual(empty_classroom.group_id, target_group.id)
        self.assertEqual(empty_classroom.staff_id, self.admin.id)

    @patch("academics.views.build_execute_promotion_use_case")
    def test_unexpected_promotion_error_does_not_leak_internal_details(
        self,
        build_use_case,
    ):
        build_use_case.return_value.execute.side_effect = RuntimeError(
            "secret constraint enrollments_student_id_period_group_id_uniq"
        )
        response = self.client.post(
            "/api/academics/promotions/execute/",
            {
                "source_classroom_id": str(self.classroom.id),
                "period": "2026-2027",
                "students": [
                    {"student_id": str(self.student.id), "action": "promote"}
                ],
                "target_group": {
                    "school_grade_id": str(self.school_grade.id),
                    "letter": "B",
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, 500)
        self.assertNotIn("secret constraint", response.data["detail"])
