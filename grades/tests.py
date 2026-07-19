from datetime import date
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from academics.models import ClassRoom, Enrollment, Group, SchoolGrade, Subject
from assignments.models import Assignment
from grades.application.dto.grade_dto import CreateGradeCommand
from grades.application.use_cases.delete_grade import DeleteGradeUseCase
from grades.application.use_cases.grade_use_cases import CreateGradeUseCase
from grades.application.use_cases.update_grade import UpdateGradeUseCase
from grades.domain.exceptions.grade_exceptions import GradeNotFoundError
from grades.models import GradingCriteria, StudentGrade
from staff.models import Staff
from students.models import Student


class _InMemoryGradeRepository:
    def list_grades(self, class_room_id=None):
        return []

    def get_grade(self, grade_id):
        return None

    def create_grade(self, command: CreateGradeCommand):
        return {"student": command.student_id, "score": str(command.score)}

    def update_grade(self, command):
        if command.grade_id != 1:
            raise GradeNotFoundError("Grade not found")
        return {"id": 1, "score": str(command.score or Decimal("8"))}

    def delete_grade(self, grade_id: int):
        if grade_id != 1:
            raise GradeNotFoundError("Grade not found")


class GradeUseCaseTests(TestCase):
    def test_create_grade_validates_required_fields(self):
        use_case = CreateGradeUseCase(repository=_InMemoryGradeRepository())
        command = CreateGradeCommand(
            student_id="",
            class_room_id="room",
            assignment_id="assign",
            subject_id="subject",
            score=Decimal("8.5"),
            date=date.today(),
            description="quiz",
        )
        with self.assertRaises(ValueError):
            use_case.execute(command)

    def test_update_grade_raises_not_found(self):
        use_case = UpdateGradeUseCase(repository=_InMemoryGradeRepository())
        with self.assertRaises(GradeNotFoundError):
            use_case.execute(type("Cmd", (), {"grade_id": 999, "score": Decimal("7"), "description": None})())

    def test_delete_grade_raises_not_found(self):
        use_case = DeleteGradeUseCase(repository=_InMemoryGradeRepository())
        with self.assertRaises(GradeNotFoundError):
            use_case.execute(999)


class GradeEndpointsSmokeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = Staff.objects.create_user(
            username="teacher-grades",
            password="pass1234",
            first_name="Raul",
            last_name="Mendez",
        )
        self.admin = Staff.objects.create_user(
            username="admin-grades",
            password="pass1234",
            role="Admin",
        )
        self.school_grade = SchoolGrade.objects.create(name="3ro")
        self.group = Group.objects.create(letter="C", school_grade=self.school_grade)
        self.class_room = ClassRoom.objects.create(staff=self.staff, group=self.group)
        self.subject = Subject.objects.create(name="Math", school_grade=self.school_grade)
        self.grading_criteria = GradingCriteria.objects.create(
            name="Exams",
            class_room=self.class_room,
            percentage=Decimal("100.00"),
        )
        self.student = Student.objects.create(
            first_name="Pedro",
            last_name="Torres",
            curp="TOPP140101HDFRRDA0",
            tutor_name="Ana Torres",
            tutor_phone="5551234567",
            tutor_relationship="Madre",
            enrollment_number="E20268888",
            date_of_birth="2014-11-20",
            gender="M",
            state="active",
        )
        self.assignment = Assignment.objects.create(
            title="Exam 1",
            class_room=self.class_room,
            subject=self.subject,
            grading_criteria=self.grading_criteria,
            max_score=Decimal("10.00"),
            due_date=date.today(),
        )
        Enrollment.objects.create(
            student=self.student,
            group=self.group,
            period="2026",
            state="activo",
        )
        self.client.force_authenticate(user=self.staff)

    def _create_foreign_resources(self, suffix):
        other_teacher = Staff.objects.create_user(
            username=f"foreign-teacher-grades-{suffix}",
            password="pass1234",
            role="Teacher",
        )
        other_group = Group.objects.create(
            letter=f"F{str(suffix)[:4]}",
            school_grade=self.school_grade,
        )
        other_classroom = ClassRoom.objects.create(
            staff=other_teacher,
            group=other_group,
        )
        other_student = Student.objects.create(
            first_name="Foreign",
            last_name="Student",
            curp=f"FOREIGN{suffix:0>11}"[:18],
            tutor_name="Tutor",
            tutor_phone="5550000000",
            tutor_relationship="Tutor",
            enrollment_number=f"E-F-{suffix}",
            date_of_birth="2015-01-01",
            gender="X",
            state="activo",
        )
        Enrollment.objects.create(
            student=other_student,
            group=other_group,
            period="2026",
            state="activo",
        )
        other_criteria = GradingCriteria.objects.create(
            name=f"Foreign criteria {suffix}",
            class_room=other_classroom,
            percentage=Decimal("100.00"),
        )
        other_assignment = Assignment.objects.create(
            title=f"Foreign assignment {suffix}",
            class_room=other_classroom,
            subject=self.subject,
            grading_criteria=other_criteria,
            max_score=Decimal("10.00"),
            due_date=date.today(),
        )
        other_grade = StudentGrade.objects.create(
            student=other_student,
            class_room=other_classroom,
            subject=self.subject,
            assignment=other_assignment,
            score=Decimal("8.00"),
            date=date.today(),
        )
        return (
            other_classroom,
            other_student,
            other_criteria,
            other_assignment,
            other_grade,
        )

    def _create_assignment_in_another_owned_classroom(self):
        group = Group.objects.create(letter="O", school_grade=self.school_grade)
        classroom = ClassRoom.objects.create(staff=self.staff, group=group)
        criteria = GradingCriteria.objects.create(
            name="Other owned criteria",
            class_room=classroom,
            percentage=Decimal("100.00"),
        )
        assignment = Assignment.objects.create(
            title="Other owned assignment",
            class_room=classroom,
            subject=self.subject,
            grading_criteria=criteria,
            max_score=Decimal("10.00"),
            due_date=date.today(),
        )
        return classroom, assignment

    def test_anonymous_user_cannot_list_classroom_grades(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            f"/api/grades/classroom/{self.class_room.id}/"
        )

        self.assertEqual(response.status_code, 401)

    def test_teacher_cannot_access_another_classroom_grades(self):
        other_teacher = Staff.objects.create_user(
            username="other-teacher-grades",
            password="pass1234",
            role="Teacher",
        )
        other_group = Group.objects.create(letter="D", school_grade=self.school_grade)
        other_classroom = ClassRoom.objects.create(
            staff=other_teacher,
            group=other_group,
        )

        response = self.client.get(
            f"/api/grades/classroom/{other_classroom.id}/"
        )

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_update_grade_from_another_classroom(self):
        other_teacher = Staff.objects.create_user(
            username="update-other-teacher-grades",
            password="pass1234",
            role="Teacher",
        )
        other_group = Group.objects.create(letter="E", school_grade=self.school_grade)
        other_classroom = ClassRoom.objects.create(
            staff=other_teacher,
            group=other_group,
        )
        other_criteria = GradingCriteria.objects.create(
            name="Other exams",
            class_room=other_classroom,
            percentage=Decimal("100.00"),
        )
        other_assignment = Assignment.objects.create(
            title="Other exam",
            class_room=other_classroom,
            subject=self.subject,
            grading_criteria=other_criteria,
            max_score=Decimal("10.00"),
            due_date=date.today(),
        )
        grade = StudentGrade.objects.create(
            student=self.student,
            class_room=other_classroom,
            subject=self.subject,
            assignment=other_assignment,
            score=Decimal("8.00"),
            date=date.today(),
        )

        response = self.client.put(
            f"/api/grades/{grade.id}/",
            {"score": "10.00"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        grade.refresh_from_db()
        self.assertEqual(grade.score, Decimal("8.00"))

    def test_teacher_cannot_use_global_grade_listing(self):
        response = self.client.get("/api/grades/")

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_post_grade_to_another_classroom(self):
        classroom, student, _, assignment, _ = self._create_foreign_resources("post")

        response = self.client.post(
            "/api/grades/",
            {
                "student": str(student.id),
                "subject": str(self.subject.id),
                "class_room": str(classroom.id),
                "assignment": str(assignment.id),
                "score": "9.00",
                "date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_link_foreign_assignment_to_own_grade(self):
        _, _, _, assignment, _ = self._create_foreign_resources("link")

        response = self.client.post(
            "/api/grades/",
            {
                "student": str(self.student.id),
                "subject": str(self.subject.id),
                "class_room": str(self.class_room.id),
                "assignment": str(assignment.id),
                "score": "9.00",
                "date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_grade_student_from_foreign_classroom(self):
        _, student, _, _, _ = self._create_foreign_resources("student-link")

        response = self.client.post(
            "/api/grades/",
            {
                "student": str(student.id),
                "subject": str(self.subject.id),
                "class_room": str(self.class_room.id),
                "assignment": str(self.assignment.id),
                "score": "9.00",
                "date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_cross_link_student_from_another_owned_classroom(self):
        other_classroom, _ = self._create_assignment_in_another_owned_classroom()
        student = Student.objects.create(
            first_name="Other owned",
            last_name="Student",
            curp="GRADEOWNEDSTUDENT1",
            tutor_name="Tutor",
            tutor_phone="5550000000",
            tutor_relationship="Tutor",
            enrollment_number="E-GRADE-OWNED",
            date_of_birth="2015-01-01",
            gender="X",
            state="activo",
        )
        Enrollment.objects.create(
            student=student,
            group=other_classroom.group,
            period="2026",
            state="activo",
        )

        response = self.client.post(
            "/api/grades/",
            {
                "student": str(student.id),
                "subject": str(self.subject.id),
                "class_room": str(self.class_room.id),
                "assignment": str(self.assignment.id),
                "score": "9.00",
                "date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_grade_rejects_assignment_from_another_owned_classroom(self):
        _, assignment = self._create_assignment_in_another_owned_classroom()

        response = self.client.post(
            "/api/grades/",
            {
                "student": str(self.student.id),
                "subject": str(self.subject.id),
                "class_room": str(self.class_room.id),
                "assignment": str(assignment.id),
                "score": "9.00",
                "date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_grade_subject_must_match_assignment_subject(self):
        another_subject = Subject.objects.create(
            name="Science",
            school_grade=self.school_grade,
        )

        response = self.client.post(
            "/api/grades/",
            {
                "student": str(self.student.id),
                "subject": str(another_subject.id),
                "class_room": str(self.class_room.id),
                "assignment": str(self.assignment.id),
                "score": "9.00",
                "date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_admin_cannot_grade_student_not_enrolled_in_classroom(self):
        student = Student.objects.create(
            first_name="Not",
            last_name="Enrolled",
            curp="GRADENOTENROLLED01",
            tutor_name="Tutor",
            tutor_phone="5550000000",
            tutor_relationship="Tutor",
            enrollment_number="E-G-NE-1",
            date_of_birth="2015-01-01",
            gender="X",
            state="activo",
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/grades/",
            {
                "student": str(student.id),
                "subject": str(self.subject.id),
                "class_room": str(self.class_room.id),
                "assignment": str(self.assignment.id),
                "score": "9.00",
                "date": str(date.today()),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_teacher_cannot_delete_grade_from_another_classroom(self):
        _, _, _, _, grade = self._create_foreign_resources("delete")

        response = self.client.delete(f"/api/grades/{grade.id}/")

        self.assertEqual(response.status_code, 403)
        self.assertTrue(StudentGrade.objects.filter(pk=grade.id).exists())

    def test_teacher_cannot_update_criteria_from_another_classroom(self):
        _, _, criteria, _, _ = self._create_foreign_resources("criteria-update")

        response = self.client.put(
            f"/api/grades/grading-criteria/{criteria.id}/",
            {"name": "Forbidden"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_delete_criteria_from_another_classroom(self):
        _, _, criteria, _, _ = self._create_foreign_resources("criteria-delete")

        response = self.client.delete(
            f"/api/grades/grading-criteria/{criteria.id}/"
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(GradingCriteria.objects.filter(pk=criteria.id).exists())

    def test_teacher_cannot_move_criteria_between_assigned_classrooms(self):
        other_group = Group.objects.create(letter="T", school_grade=self.school_grade)
        other_classroom = ClassRoom.objects.create(
            staff=self.staff,
            group=other_group,
        )

        response = self.client.put(
            f"/api/grades/grading-criteria/{self.grading_criteria.id}/",
            {"class_room": str(other_classroom.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.grading_criteria.refresh_from_db()
        self.assertEqual(self.grading_criteria.class_room_id, self.class_room.id)

    def test_teacher_cannot_move_criteria_to_foreign_classroom(self):
        classroom, _, _, _, _ = self._create_foreign_resources("criteria-move")

        response = self.client.put(
            f"/api/grades/grading-criteria/{self.grading_criteria.id}/",
            {"class_room": str(classroom.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.grading_criteria.refresh_from_db()
        self.assertEqual(self.grading_criteria.class_room_id, self.class_room.id)

    def test_admin_cannot_move_criteria_that_has_assignments(self):
        other_group = Group.objects.create(letter="A2", school_grade=self.school_grade)
        other_classroom = ClassRoom.objects.create(
            staff=self.staff,
            group=other_group,
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.put(
            f"/api/grades/grading-criteria/{self.grading_criteria.id}/",
            {"class_room": str(other_classroom.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.grading_criteria.refresh_from_db()
        self.assertEqual(self.grading_criteria.class_room_id, self.class_room.id)

    def test_create_grade_endpoint_returns_201(self):
        response = self.client.post("/api/grades/", {
            "student": str(self.student.id),
            "subject": str(self.subject.id),
            "class_room": str(self.class_room.id),
            "assignment": str(self.assignment.id),
            "score": "9.2",
            "date": str(date.today()),
        }, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(str(response.data["score"]), "9.20")

    def test_list_grades_by_classroom_returns_200(self):
        self.client.post("/api/grades/", {
            "student": str(self.student.id),
            "subject": str(self.subject.id),
            "class_room": str(self.class_room.id),
            "assignment": str(self.assignment.id),
            "score": "8.0",
            "date": str(date.today()),
        }, format="json")
        response = self.client.get(f"/api/grades/classroom/{self.class_room.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_update_grade_endpoint_returns_200(self):
        create_response = self.client.post("/api/grades/", {
            "student": str(self.student.id),
            "subject": str(self.subject.id),
            "class_room": str(self.class_room.id),
            "assignment": str(self.assignment.id),
            "score": "7.0",
            "date": str(date.today()),
        }, format="json")
        response = self.client.put(
            f"/api/grades/{create_response.data['id']}/",
            {"score": "8.5", "description": "Updated"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.data["score"]), "8.50")

    def test_delete_grade_endpoint_returns_204(self):
        create_response = self.client.post("/api/grades/", {
            "student": str(self.student.id),
            "subject": str(self.subject.id),
            "class_room": str(self.class_room.id),
            "assignment": str(self.assignment.id),
            "score": "7.0",
            "date": str(date.today()),
        }, format="json")
        response = self.client.delete(f"/api/grades/{create_response.data['id']}/")
        self.assertEqual(response.status_code, 204)
