from datetime import date

from django.test import TestCase
from rest_framework.test import APIClient

from academics.models import Group, SchoolGrade
from staff.models import Staff
from students.application.dto.student_dto import CreateStudentCommand
from students.application.use_cases.create_student import CreateStudentWithEnrollmentUseCase
from students.application.use_cases.delete_student import DeleteStudentUseCase
from students.application.use_cases.get_students import GetStudentDetailUseCase
from students.application.use_cases.update_student import UpdateStudentUseCase
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

	def update_student(self, command):
		if command.student_id not in self._items:
			raise StudentNotFoundError("Student not found")
		item = self._items[command.student_id]
		if command.first_name is not None:
			item["first_name"] = command.first_name
		if command.last_name is not None:
			item["last_name"] = command.last_name
		return item

	def delete_student(self, student_id: str):
		if student_id not in self._items:
			raise StudentNotFoundError("Student not found")
		del self._items[student_id]


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
			curp="Suab850310Mtcrra09",
			tutor_name="Juan Perez",
			tutor_phone="1234567890",
			tutor_relationship="Padre",
			date_of_birth=date(2014, 1, 1),
			gender="M",
			state="active",
			group_id="1",
			period="2026",
		)

		with self.assertRaises(ValueError):
			use_case.execute(command)

	def test_update_student_raises_not_found(self):
		use_case = UpdateStudentUseCase(repository=_InMemoryStudentRepository())

		with self.assertRaises(StudentNotFoundError):
			use_case.execute(type("Cmd", (), {"student_id": "missing", "first_name": "Ana", "last_name": None})())

	def test_delete_student_raises_not_found(self):
		use_case = DeleteStudentUseCase(repository=_InMemoryStudentRepository())

		with self.assertRaises(StudentNotFoundError):
			use_case.execute("missing")


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
			"curp": "Suab850512Mtcrra09",
			"tutor_name": "Juan Suarez",
			"tutor_phone": "1234567890",
			"tutor_relationship": "Padre",
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

	def test_update_student_endpoint_returns_200(self):
		student = Student.objects.create(
			first_name="Pablo",
			second_name="Andres",
			last_name="Rios",
			enrollment_number="E20260002",
			date_of_birth="2014-01-02",
			gender="M",
			state="active",
		)

		response = self.client.put(
			f"/api/students/{student.id}/",
			{"first_name": "Pablo-Updated", "last_name": "Rios", "gender": "M", "state": "active"},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["first_name"], "Pablo-Updated")

	def test_patch_student_endpoint_returns_200(self):
		student = Student.objects.create(
			first_name="Julia",
			second_name="Maria",
			last_name="Luna",
			enrollment_number="E20260003",
			date_of_birth="2014-01-03",
			gender="F",
			state="active",
		)

		response = self.client.patch(
			f"/api/students/{student.id}/",
			{"first_name": "Julia2"},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["first_name"], "Julia2")

	def test_delete_student_endpoint_returns_204(self):
		student = Student.objects.create(
			first_name="Mario",
			second_name="Jose",
			last_name="Navas",
			enrollment_number="E20260004",
			date_of_birth="2014-01-04",
			gender="M",
			state="active",
		)

		response = self.client.delete(f"/api/students/{student.id}/")

		self.assertEqual(response.status_code, 204)
