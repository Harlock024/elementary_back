from datetime import date
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from academics.models import ClassRoom, Enrollment, Group, SchoolGrade, Subject
from assignments.models import Assignment
from grades.models import GradingCriteria
from staff.models import Staff
from students.models import Student


class AssignmentAuthorizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = Staff.objects.create_user(
            username="teacher-assignments",
            password="pass1234",
            role="Teacher",
        )
        self.other_teacher = Staff.objects.create_user(
            username="other-teacher-assignments",
            password="pass1234",
            role="Teacher",
        )
        school_grade = SchoolGrade.objects.create(name="4to")
        self.school_grade = school_grade
        own_group = Group.objects.create(letter="A", school_grade=school_grade)
        other_group = Group.objects.create(letter="B", school_grade=school_grade)
        self.own_group = own_group
        self.other_group = other_group
        self.classroom = ClassRoom.objects.create(
            staff=self.teacher,
            group=own_group,
        )
        self.other_classroom = ClassRoom.objects.create(
            staff=self.other_teacher,
            group=other_group,
        )
        self.subject = Subject.objects.create(name="Math", school_grade=school_grade)
        self.own_criteria = GradingCriteria.objects.create(
            name="Own homework",
            class_room=self.classroom,
            percentage=Decimal("100.00"),
        )
        other_criteria = GradingCriteria.objects.create(
            name="Homework",
            class_room=self.other_classroom,
            percentage=Decimal("100.00"),
        )
        self.other_assignment = Assignment.objects.create(
            class_room=self.other_classroom,
            subject=self.subject,
            grading_criteria=other_criteria,
            title="Private assignment",
            due_date=date.today(),
            max_score=Decimal("10.00"),
        )
        self.own_assignment = Assignment.objects.create(
            class_room=self.classroom,
            subject=self.subject,
            grading_criteria=self.own_criteria,
            title="Own assignment today",
            due_date=date.today(),
            max_score=Decimal("10.00"),
        )
        self.tomorrow_assignment = Assignment.objects.create(
            class_room=self.classroom,
            subject=self.subject,
            grading_criteria=self.own_criteria,
            title="Own assignment tomorrow",
            due_date=date.fromordinal(date.today().toordinal() + 1),
            max_score=Decimal("10.00"),
        )
        self.student = Student.objects.create(
            first_name="Assigned",
            last_name="Student",
            curp="ASSIGNMENTSTUDENT1",
            tutor_name="Tutor",
            tutor_phone="5550000000",
            tutor_relationship="Tutor",
            enrollment_number="E-ASG-1",
            date_of_birth="2015-01-01",
            gender="X",
            state="activo",
        )
        Enrollment.objects.create(
            student=self.student,
            group=self.own_group,
            period="2026",
            state="activo",
        )
        self.client.force_authenticate(user=self.teacher)

    def _create_criteria_in_another_owned_classroom(self):
        group = Group.objects.create(letter="C", school_grade=self.school_grade)
        classroom = ClassRoom.objects.create(staff=self.teacher, group=group)
        criteria = GradingCriteria.objects.create(
            name="Other owned criteria",
            class_room=classroom,
            percentage=Decimal("100.00"),
        )
        return classroom, criteria

    def test_anonymous_user_cannot_list_classroom_assignments(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            f"/api/assignments/classroom/{self.classroom.id}/"
        )

        self.assertEqual(response.status_code, 401)

    def test_teacher_cannot_list_another_classroom_assignments(self):
        response = self.client.get(
            f"/api/assignments/classroom/{self.other_classroom.id}/"
        )

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_patch_assignment_from_another_classroom(self):
        response = self.client.patch(
            f"/api/assignments/{self.other_assignment.id}/",
            {"title": "Unauthorized change"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.other_assignment.refresh_from_db()
        self.assertEqual(self.other_assignment.title, "Private assignment")

    def test_teacher_cannot_delete_assignment_from_another_classroom(self):
        response = self.client.delete(
            f"/api/assignments/{self.other_assignment.id}/"
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(
            Assignment.objects.filter(pk=self.other_assignment.id).exists()
        )

    def test_teacher_cannot_post_assignment_to_another_classroom(self):
        response = self.client.post(
            f"/api/assignments/classroom/{self.other_classroom.id}/",
            {
                "subject_id": str(self.subject.id),
                "grading_criteria_id": str(self.other_assignment.grading_criteria_id),
                "title": "Forbidden",
                "due_date": str(date.today()),
                "max_score": "10",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_link_foreign_criteria_to_own_assignment(self):
        response = self.client.post(
            f"/api/assignments/classroom/{self.classroom.id}/",
            {
                "subject_id": str(self.subject.id),
                "grading_criteria_id": str(self.other_assignment.grading_criteria_id),
                "title": "Cross classroom",
                "due_date": str(date.today()),
                "max_score": "10",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_assignment_rejects_criteria_from_another_owned_classroom(self):
        _, criteria = self._create_criteria_in_another_owned_classroom()

        response = self.client.post(
            f"/api/assignments/classroom/{self.classroom.id}/",
            {
                "subject_id": str(self.subject.id),
                "grading_criteria_id": str(criteria.id),
                "title": "Cross owned classroom",
                "due_date": str(date.today()),
                "max_score": "10",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_assignment_subject_must_match_classroom_school_grade(self):
        other_grade = SchoolGrade.objects.create(name="5to")
        other_subject = Subject.objects.create(
            name="Other-grade subject",
            school_grade=other_grade,
        )

        response = self.client.post(
            f"/api/assignments/classroom/{self.classroom.id}/",
            {
                "subject_id": str(other_subject.id),
                "grading_criteria_id": str(self.own_criteria.id),
                "title": "Wrong subject",
                "due_date": str(date.today()),
                "max_score": "10",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_patch_rejects_criteria_from_another_classroom(self):
        response = self.client.patch(
            f"/api/assignments/{self.own_assignment.id}/",
            {"grading_criteria_id": str(self.other_assignment.grading_criteria_id)},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.own_assignment.refresh_from_db()
        self.assertEqual(self.own_assignment.grading_criteria_id, self.own_criteria.id)

    def test_patch_rejects_criteria_from_another_owned_classroom(self):
        _, criteria = self._create_criteria_in_another_owned_classroom()

        response = self.client.patch(
            f"/api/assignments/{self.own_assignment.id}/",
            {"grading_criteria_id": str(criteria.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.own_assignment.refresh_from_db()
        self.assertEqual(self.own_assignment.grading_criteria_id, self.own_criteria.id)

    def test_patch_rejects_subject_from_another_school_grade(self):
        other_grade = SchoolGrade.objects.create(name="6to")
        other_subject = Subject.objects.create(
            name="Foreign subject",
            school_grade=other_grade,
        )

        response = self.client.patch(
            f"/api/assignments/{self.own_assignment.id}/",
            {"subject_id": str(other_subject.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.own_assignment.refresh_from_db()
        self.assertEqual(self.own_assignment.subject_id, self.subject.id)

    def test_teacher_cannot_use_global_assignment_listing(self):
        response = self.client.get("/api/assignments/")

        self.assertEqual(response.status_code, 403)

    def test_teacher_can_list_assigned_classroom(self):
        response = self.client.get(
            f"/api/assignments/classroom/{self.classroom.id}/"
        )

        self.assertEqual(response.status_code, 200)

    def test_student_date_route_filters_due_date(self):
        response = self.client.get(
            f"/api/assignments/student/{self.student.id}/date/{date.today()}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["id"] for item in response.data],
            [str(self.own_assignment.id)],
        )

    def test_student_date_route_does_not_leak_foreign_assignments(self):
        Enrollment.objects.create(
            student=self.student,
            group=self.other_group,
            period="2025",
            state="inactivo",
        )

        response = self.client.get(
            f"/api/assignments/student/{self.student.id}/date/{date.today()}/"
        )

        self.assertEqual(response.status_code, 200)
        returned_ids = {item["id"] for item in response.data}
        self.assertIn(str(self.own_assignment.id), returned_ids)
        self.assertNotIn(str(self.other_assignment.id), returned_ids)
