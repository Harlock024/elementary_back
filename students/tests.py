from datetime import date

from django.test import TestCase
from rest_framework.test import APIClient

from academics.models import Group, SchoolGrade
from staff.models import Staff
from students.application.dto.student_dto import CreateStudentCommand
from students.application.use_cases.create_student import CreateStudentWithEnrollmentUseCase
from students.application.use_cases.get_students import GetStudentDetailUseCase
from students.domain.exceptions.student_exceptions import StudentNotFoundError
from students.models import Student


class _InMemoryStudentRepository:
	def __init__(self):
		self._items = {
			"1": {"id": "1", "first_name": "Ana", "last_name": "Lopez"}
		}

	def list_students_detail(self):
		return list(self._items.values())

	def get_student_detail(self, student_id: str):
		return self._items.get(student_id)

	def create_student_with_enrollment(self, command: CreateStudentCommand):
		return {
			"id": "new",
			"first_name": command.first_name,
			"last_name": command.last_name,
			"state": command.state,
		}


class StudentUseCaseTests(TestCase):
	def test_get_student_detail_raises_not_found(self):
		use_case = GetStudentDetailUseCase(repository=_InMemoryStudentRepository())

		with self.assertRaises(StudentNotFoundError):
			use_case.execute("missing")

	def test_create_student_validates_required_fields(self):
		use_case = CreateStudentWithEnrollmentUseCase(repository=_InMemoryStudentRepository())
		command = CreateStudentCommand(
			first_name="",
			second_name=None,
			last_name="Perez",
			date_of_birth=date(2014, 1, 1),
			gender="M",
			state="active",
			group_id="1",
			period="2026",
		)

		with self.assertRaises(ValueError):
			use_case.execute(command)


class StudentEndpointsSmokeTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.admin = Staff.objects.create_user(
			username="admin-smoke",
			password="test1234",
			role="Admin",
		)
		self.client.force_authenticate(user=self.admin)

		self.school_grade = SchoolGrade.objects.create(name="1ro")
		self.group = Group.objects.create(letter="A", school_grade=self.school_grade)

	def test_create_student_endpoint_returns_201(self):
		payload = {
			"first_name": "Maria",
			"second_name": "Elena",
			"last_name": "Suarez",
			"date_of_birth": "2014-05-12",
			"gender": "F",
			"state": "active",
			"group_id": str(self.group.id),
			"period": "2026",
		}

		response = self.client.post("/api/students/", payload, format="json")

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["first_name"], payload["first_name"])
		self.assertTrue(Student.objects.filter(last_name="Suarez").exists())

	def test_get_students_endpoint_returns_200(self):
		Student.objects.create(
			first_name="Luis",
			second_name="Alberto",
			last_name="Diaz",
			enrollment_number="E20260001",
			date_of_birth="2014-03-01",
			gender="M",
			state="active",
		)

		response = self.client.get("/api/students/")

		self.assertEqual(response.status_code, 200)
		self.assertTrue(len(response.data) >= 1)
