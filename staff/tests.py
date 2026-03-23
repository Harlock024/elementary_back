from django.test import TestCase
from rest_framework.test import APIClient

from staff.application.dto.staff_dto import CreateStaffCommand
from staff.application.use_cases.delete_staff import DeleteStaffUseCase
from staff.application.use_cases.staff_use_cases import CreateStaffUseCase
from staff.application.use_cases.update_staff import UpdateStaffUseCase
from staff.domain.exceptions.staff_exceptions import StaffNotFoundError
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

	def update_staff(self, command):
		if command.staff_id != "1":
			raise StaffNotFoundError("Staff not found")
		return {
			"id": "1",
			"first_name": command.first_name or "Ana",
			"last_name": command.last_name or "Lopez",
		}

	def delete_staff(self, staff_id: str):
		if staff_id != "1":
			raise StaffNotFoundError("Staff not found")


class StaffUseCaseTests(TestCase):
	def test_create_staff_validates_required_fields(self):
		use_case = CreateStaffUseCase(repository=_InMemoryStaffRepository())
		command = CreateStaffCommand(id=None, first_name="", last_name="Ramos")

		with self.assertRaises(ValueError):
			use_case.execute(command)

	def test_update_staff_raises_not_found(self):
		use_case = UpdateStaffUseCase(repository=_InMemoryStaffRepository())

		with self.assertRaises(StaffNotFoundError):
			use_case.execute(type("Cmd", (), {"staff_id": "missing", "first_name": "A", "last_name": None, "username": None, "role": None})())

	def test_delete_staff_raises_not_found(self):
		use_case = DeleteStaffUseCase(repository=_InMemoryStaffRepository())

		with self.assertRaises(StaffNotFoundError):
			use_case.execute("missing")


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

	def test_update_staff_endpoint_returns_200(self):
		staff = Staff.objects.create_user(
			username="staff-update-user",
			password="pass1234",
			first_name="Erika",
			last_name="Ramos",
		)

		response = self.client.put(
			f"/api/staff/{staff.id}/",
			{"first_name": "Erika2", "last_name": "Ramos", "version": staff.version},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["first_name"], "Erika2")

	def test_delete_staff_endpoint_returns_204(self):
		staff = Staff.objects.create_user(
			username="staff-delete-user",
			password="pass1234",
			first_name="Marco",
			last_name="Paz",
		)

		response = self.client.delete(f"/api/staff/{staff.id}/")

		self.assertEqual(response.status_code, 204)
