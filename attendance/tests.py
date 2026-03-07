from django.test import TestCase
from rest_framework.test import APIClient

from academics.models import ClassRoom, Group, SchoolGrade
from attendance.application.dto.attendance_dto import CreateAttendanceCommand
from attendance.application.use_cases.attendance_use_cases import CreateAttendanceUseCase
from attendance.application.use_cases.update_attendance import UpdateAttendanceUseCase
from attendance.domain.exceptions.attendance_exceptions import AttendanceNotFoundError
from attendance.models import CatalogTypeAtendance
from staff.models import Staff
from students.models import Student


class _InMemoryAttendanceRepository:
	def list_attendance(self, class_id=None, attendance_date=None, student_id=None):
		return []

	def create_attendance(self, command: CreateAttendanceCommand):
		return {
			"date": str(command.attendance_date),
			"student": command.student_id,
			"state_code": command.state_code_id,
		}

	def update_attendance(self, command):
		if command.attendance_id != "1":
			raise AttendanceNotFoundError("Attendance record not found")
		return {"id": "1", "state_code": command.state_code_id or "state"}


class AttendanceUseCaseTests(TestCase):
	def test_create_attendance_validates_required_fields(self):
		use_case = CreateAttendanceUseCase(repository=_InMemoryAttendanceRepository())
		command = CreateAttendanceCommand(
			student_id="",
			state_code_id="state",
			class_id="class",
			attendance_date="2026-03-01",
		)

		with self.assertRaises(ValueError):
			use_case.execute(command)

	def test_update_attendance_raises_not_found(self):
		use_case = UpdateAttendanceUseCase(repository=_InMemoryAttendanceRepository())

		with self.assertRaises(AttendanceNotFoundError):
			use_case.execute(type("Cmd", (), {"attendance_id": "missing", "state_code_id": "x"})())


class AttendanceEndpointsSmokeTests(TestCase):
	def setUp(self):
		self.client = APIClient()

		self.staff = Staff.objects.create_user(
			username="teacher-attendance",
			password="pass1234",
			first_name="Marta",
			last_name="Rios",
		)
		self.school_grade = SchoolGrade.objects.create(name="2do")
		self.group = Group.objects.create(letter="B", school_grade=self.school_grade)
		self.class_room = ClassRoom.objects.create(staff=self.staff, group=self.group)

		self.student = Student.objects.create(
			first_name="Nora",
			second_name="Elena",
			last_name="Campos",
			enrollment_number="E20269999",
			date_of_birth="2015-03-10",
			gender="F",
			state="active",
		)
		self.state_code = CatalogTypeAtendance.objects.create(
			code="present",
			description="Present",
		)

	def test_create_attendance_endpoint_returns_201(self):
		payload = {
			"student": str(self.student.id),
			"state_code": str(self.state_code.id),
			"date": "2026-03-01",
		}

		response = self.client.post(
			f"/api/attendances/classroom/{self.class_room.id}/",
			payload,
			format="json",
		)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["date"], payload["date"])

	def test_list_attendance_by_class_date_returns_200(self):
		self.client.post(
			f"/api/attendances/classroom/{self.class_room.id}/",
			{
				"student": str(self.student.id),
				"state_code": str(self.state_code.id),
				"date": "2026-03-02",
			},
			format="json",
		)

		response = self.client.get(
			f"/api/attendances/classroom/{self.class_room.id}/date/2026-03-02/"
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)

	def test_patch_attendance_endpoint_returns_200(self):
		create_response = self.client.post(
			f"/api/attendances/classroom/{self.class_room.id}/",
			{
				"student": str(self.student.id),
				"state_code": str(self.state_code.id),
				"date": "2026-03-03",
			},
			format="json",
		)

		new_state = CatalogTypeAtendance.objects.create(code="late", description="Late")
		response = self.client.patch(
			f"/api/attendances/{create_response.data['id']}/",
			{"state_code": str(new_state.id)},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
