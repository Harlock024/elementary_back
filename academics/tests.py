from django.test import TestCase
from rest_framework.test import APIClient

from academics.application.dto.school_grade_dto import CreateSchoolGradeCommand
from academics.application.use_cases.school_grade_use_cases import CreateSchoolGradeUseCase
from staff.models import Staff


class _InMemorySchoolGradeRepository:
	def list_school_grades(self):
		return [{"id": "1", "name": "1ro"}]

	def get_school_grade(self, school_grade_id):
		return None

	def create_school_grade(self, command: CreateSchoolGradeCommand):
		return {"id": "new", "name": command.name}


class SchoolGradeUseCaseTests(TestCase):
	def test_create_school_grade_validates_name(self):
		use_case = CreateSchoolGradeUseCase(repository=_InMemorySchoolGradeRepository())
		command = CreateSchoolGradeCommand(name="")

		with self.assertRaises(ValueError):
			use_case.execute(command)


class SchoolGradeEndpointsSmokeTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.admin = Staff.objects.create_user(
			username="admin-academics",
			password="pass1234",
			role="Admin",
		)
		self.client.force_authenticate(user=self.admin)

	def test_create_school_grade_endpoint_returns_201(self):
		payload = {"name": "6to"}

		response = self.client.post("/api/academics/school-grades/", payload, format="json")

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["name"], payload["name"])

	def test_list_school_grade_endpoint_returns_200(self):
		self.client.post("/api/academics/school-grades/", {"name": "1ro"}, format="json")

		response = self.client.get("/api/academics/school-grades/")

		self.assertEqual(response.status_code, 200)
		self.assertTrue(len(response.data) >= 1)
