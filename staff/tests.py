from django.test import TestCase
from rest_framework.test import APIClient

from staff.application.dto.staff_dto import CreateStaffCommand
from staff.application.use_cases.staff_use_cases import CreateStaffUseCase
from staff.models import Staff


class _InMemoryStaffRepository:
	def list_staff(self):
		return [{"id": "1", "first_name": "Ana", "last_name": "Lopez"}]

	def create_staff(self, command: CreateStaffCommand):
		return {
			"id": "new",
			"first_name": command.first_name,
			"last_name": command.last_name,
		}


class StaffUseCaseTests(TestCase):
	def test_create_staff_validates_required_fields(self):
		use_case = CreateStaffUseCase(repository=_InMemoryStaffRepository())
		command = CreateStaffCommand(first_name="", last_name="Ramos")

		with self.assertRaises(ValueError):
			use_case.execute(command)


class StaffEndpointsSmokeTests(TestCase):
	def setUp(self):
		self.client = APIClient()

	def test_create_staff_endpoint_returns_200(self):
		payload = {"first_name": "Carlos", "last_name": "Perez"}

		response = self.client.post("/api/staff/", payload, format="json")

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["first_name"], payload["first_name"])
		self.assertTrue(
			Staff.objects.filter(username="carlos_perez").exists()
			or Staff.objects.filter(first_name="Carlos", last_name="Perez").exists()
		)

	def test_list_staff_endpoint_returns_200(self):
		Staff.objects.create_user(
			username="staff-list-user",
			password="pass1234",
			first_name="Luisa",
			last_name="Mora",
		)

		response = self.client.get("/api/staff/")

		self.assertEqual(response.status_code, 200)
		self.assertTrue(len(response.data) >= 1)
