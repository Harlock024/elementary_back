from datetime import date
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from academics.models import ClassRoom, Group, SchoolGrade, Subject
from assignments.models import Assignment
from grades.application.dto.grade_dto import CreateGradeCommand
from grades.application.use_cases.delete_grade import DeleteGradeUseCase
from grades.application.use_cases.grade_use_cases import CreateGradeUseCase
from grades.application.use_cases.update_grade import UpdateGradeUseCase
from grades.domain.exceptions.grade_exceptions import GradeNotFoundError
from grades.models import GradingCriteria
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
