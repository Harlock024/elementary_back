from django.test import TestCase
from rest_framework.test import APIClient

from academics.models import ClassRoom, Enrollment, Group, SchoolGrade
from attendance.application.dto.attendance_dto import CreateAttendanceCommand
from attendance.application.use_cases.attendance_use_cases import CreateAttendanceUseCase
from attendance.application.use_cases.update_attendance import UpdateAttendanceUseCase
from attendance.domain.exceptions.attendance_exceptions import AttendanceNotFoundError
from attendance.models import Attendance, CatalogTypeAtendance
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
		self.admin = Staff.objects.create_user(
			username="admin-attendance",
			password="pass1234",
			role="Admin",
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
		Enrollment.objects.create(
			student=self.student,
			group=self.group,
			period="2026",
			state="activo",
		)
		self.client.force_authenticate(user=self.staff)

	def test_anonymous_user_cannot_list_classroom_attendance(self):
		self.client.force_authenticate(user=None)

		response = self.client.get(
			f"/api/attendances/classroom/{self.class_room.id}/"
		)

		self.assertEqual(response.status_code, 401)

	def test_teacher_cannot_access_another_classroom(self):
		other_teacher = Staff.objects.create_user(
			username="other-teacher-attendance",
			password="pass1234",
			role="Teacher",
		)
		other_group = Group.objects.create(letter="C", school_grade=self.school_grade)
		other_classroom = ClassRoom.objects.create(
			staff=other_teacher,
			group=other_group,
		)

		response = self.client.get(
			f"/api/attendances/classroom/{other_classroom.id}/"
		)

		self.assertEqual(response.status_code, 403)

	def test_teacher_cannot_post_attendance_to_another_classroom(self):
		other_teacher = Staff.objects.create_user(
			username="post-other-teacher-attendance",
			password="pass1234",
			role="Teacher",
		)
		other_group = Group.objects.create(letter="E", school_grade=self.school_grade)
		other_classroom = ClassRoom.objects.create(
			staff=other_teacher,
			group=other_group,
		)

		response = self.client.post(
			f"/api/attendances/classroom/{other_classroom.id}/",
			{
				"student": str(self.student.id),
				"state_code": str(self.state_code.id),
				"date": "2026-03-05",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 403)

	def test_admin_cannot_post_attendance_for_non_enrolled_student(self):
		student = Student.objects.create(
			first_name="Not",
			last_name="Enrolled",
			curp="ATTENDANCENOTENROL",
			tutor_name="Tutor",
			tutor_phone="5550000000",
			tutor_relationship="Tutor",
			enrollment_number="E20268882",
			date_of_birth="2015-01-01",
			gender="X",
			state="activo",
		)
		self.client.force_authenticate(user=self.admin)

		response = self.client.post(
			f"/api/attendances/classroom/{self.class_room.id}/",
			{
				"student": str(student.id),
				"state_code": str(self.state_code.id),
				"date": "2026-03-09",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 400)

	def test_teacher_cannot_post_foreign_student_to_assigned_classroom(self):
		other_teacher = Staff.objects.create_user(
			username="foreign-student-teacher-attendance",
			password="pass1234",
			role="Teacher",
		)
		other_group = Group.objects.create(letter="F", school_grade=self.school_grade)
		ClassRoom.objects.create(staff=other_teacher, group=other_group)
		other_student = Student.objects.create(
			first_name="Other",
			last_name="Student",
			curp="ATTENDANCEOTHER001",
			tutor_name="Tutor",
			tutor_phone="5550000000",
			tutor_relationship="Tutor",
			enrollment_number="E20268881",
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

		response = self.client.post(
			f"/api/attendances/classroom/{self.class_room.id}/",
			{
				"student": str(other_student.id),
				"state_code": str(self.state_code.id),
				"date": "2026-03-06",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 403)

	def test_teacher_cannot_cross_link_student_from_another_owned_classroom(self):
		other_group = Group.objects.create(letter="G", school_grade=self.school_grade)
		ClassRoom.objects.create(staff=self.staff, group=other_group)
		other_student = Student.objects.create(
			first_name="Other owned",
			last_name="Student",
			curp="ATTENDANCEOWNED001",
			tutor_name="Tutor",
			tutor_phone="5550000000",
			tutor_relationship="Tutor",
			enrollment_number="E20268880",
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

		response = self.client.post(
			f"/api/attendances/classroom/{self.class_room.id}/",
			{
				"student": str(other_student.id),
				"state_code": str(self.state_code.id),
				"date": "2026-03-10",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 400)

	def test_teacher_cannot_patch_attendance_from_another_classroom(self):
		other_teacher = Staff.objects.create_user(
			username="patch-other-teacher-attendance",
			password="pass1234",
			role="Teacher",
		)
		other_group = Group.objects.create(letter="D", school_grade=self.school_grade)
		other_classroom = ClassRoom.objects.create(
			staff=other_teacher,
			group=other_group,
		)
		attendance = Attendance.objects.create(
			student=self.student,
			state_code=self.state_code,
			class_room=other_classroom,
			date="2026-03-04",
		)

		response = self.client.patch(
			f"/api/attendances/{attendance.id}/",
			{"state_code": str(self.state_code.id)},
			format="json",
		)

		self.assertEqual(response.status_code, 403)

	def test_teacher_cannot_use_global_attendance_listing(self):
		response = self.client.get("/api/attendances/")

		self.assertEqual(response.status_code, 403)

	def test_teacher_can_read_but_not_mutate_attendance_catalog(self):
		get_response = self.client.get("/api/attendances/catalog/")
		post_response = self.client.post(
			"/api/attendances/catalog/",
			{"code": "absent", "description": "Absent"},
			format="json",
		)
		patch_response = self.client.patch(
			f"/api/attendances/catalog/{self.state_code.id}/",
			{"description": "Forbidden"},
			format="json",
		)
		delete_response = self.client.delete(
			f"/api/attendances/catalog/{self.state_code.id}/"
		)

		self.assertEqual(get_response.status_code, 200)
		self.assertEqual(post_response.status_code, 403)
		self.assertEqual(patch_response.status_code, 403)
		self.assertEqual(delete_response.status_code, 403)

	def test_admin_can_patch_attendance_catalog(self):
		self.client.force_authenticate(user=self.admin)

		response = self.client.patch(
			f"/api/attendances/catalog/{self.state_code.id}/",
			{"description": "Updated safely"},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.state_code.refresh_from_db()
		self.assertEqual(self.state_code.description, "Updated safely")

	def test_admin_delete_used_attendance_catalog_returns_409(self):
		Attendance.objects.create(
			student=self.student,
			state_code=self.state_code,
			class_room=self.class_room,
			date="2026-03-07",
		)
		self.client.force_authenticate(user=self.admin)

		response = self.client.delete(
			f"/api/attendances/catalog/{self.state_code.id}/"
		)

		self.assertEqual(response.status_code, 409)
		self.assertTrue(
			CatalogTypeAtendance.objects.filter(pk=self.state_code.id).exists()
		)

	def test_admin_can_delete_unused_attendance_catalog(self):
		unused = CatalogTypeAtendance.objects.create(
			code="unused",
			description="Unused",
		)
		self.client.force_authenticate(user=self.admin)

		response = self.client.delete(f"/api/attendances/catalog/{unused.id}/")

		self.assertEqual(response.status_code, 204)
		self.assertFalse(CatalogTypeAtendance.objects.filter(pk=unused.id).exists())

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

	def test_class_date_listing_does_not_leak_other_classroom_attendance(self):
		other_teacher = Staff.objects.create_user(
			username="history-other-teacher-attendance",
			password="pass1234",
			role="Teacher",
		)
		other_group = Group.objects.create(letter="G", school_grade=self.school_grade)
		other_classroom = ClassRoom.objects.create(
			staff=other_teacher,
			group=other_group,
		)
		Attendance.objects.create(
			student=self.student,
			state_code=self.state_code,
			class_room=other_classroom,
			date="2026-03-08",
		)

		response = self.client.get(
			f"/api/attendances/classroom/{self.class_room.id}/date/2026-03-08/"
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)
		self.assertIsNone(response.data[0]["attendance"])

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
