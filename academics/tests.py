from django.test import TestCase
from rest_framework.test import APIClient

from academics.application.dto.academics_dto import (
	UpdateClassRoomCommand,
	UpdateEnrollmentCommand,
	UpdateGroupCommand,
	UpdateSubjectCommand,
)
from academics.application.dto.school_grade_dto import CreateSchoolGradeCommand
from academics.application.use_cases.academics_use_cases import (
	DeleteClassRoomUseCase,
	UpdateClassRoomUseCase,
	UpdateEnrollmentUseCase,
	UpdateGroupUseCase,
	UpdateSubjectUseCase,
)
from academics.application.use_cases.school_grade_use_cases import CreateSchoolGradeUseCase
from academics.application.use_cases.update_school_grade import UpdateSchoolGradeUseCase
from academics.domain.exceptions.academics_exceptions import (
	ClassRoomNotFoundError,
	EnrollmentNotFoundError,
	GroupNotFoundError,
	SubjectNotFoundError,
)
from academics.domain.exceptions.school_grade_exceptions import SchoolGradeNotFoundError
from academics.models import ClassRoom, Enrollment, Group, SchoolGrade, Subject
from staff.models import Staff
from students.models import Student


class _InMemorySchoolGradeRepository:
	def list_school_grades(self):
		return [{"id": "1", "name": "1ro"}]

	def get_school_grade(self, school_grade_id):
		return None

	def create_school_grade(self, command: CreateSchoolGradeCommand):
		return {"id": "new", "name": command.name}

	def update_school_grade(self, command):
		if command.school_grade_id != "1":
			raise SchoolGradeNotFoundError("School Grade not found")
		return {"id": "1", "name": command.name or "1ro"}


class SchoolGradeUseCaseTests(TestCase):
	def test_create_school_grade_validates_name(self):
		use_case = CreateSchoolGradeUseCase(repository=_InMemorySchoolGradeRepository())
		command = CreateSchoolGradeCommand(name="")

		with self.assertRaises(ValueError):
			use_case.execute(command)

	def test_update_school_grade_raises_not_found(self):
		use_case = UpdateSchoolGradeUseCase(repository=_InMemorySchoolGradeRepository())

		with self.assertRaises(SchoolGradeNotFoundError):
			use_case.execute(type("Cmd", (), {"school_grade_id": "missing", "name": "X"})())


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

	def test_update_school_grade_endpoint_returns_200(self):
		school_grade_response = self.client.post(
			"/api/academics/school-grades/",
			{"name": "2do"},
			format="json",
		)

		response = self.client.put(
			f"/api/academics/school-grades/{school_grade_response.data['id']}/",
			{"name": "2upd"},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["name"], "2upd")

	def test_patch_school_grade_endpoint_returns_200(self):
		school_grade_response = self.client.post(
			"/api/academics/school-grades/",
			{"name": "5to"},
			format="json",
		)

		response = self.client.patch(
			f"/api/academics/school-grades/{school_grade_response.data['id']}/",
			{"name": "5ptch"},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["name"], "5ptch")


class _InMemoryAcademicsRepository:
	def update_group(self, command: UpdateGroupCommand):
		if command.group_id != "1":
			raise GroupNotFoundError("Group not found")
		return {"id": "1", "letter": command.letter or "A"}

	def update_subject(self, command: UpdateSubjectCommand):
		if command.subject_id != "1":
			raise SubjectNotFoundError("Subject not found")
		return {"id": "1", "name": command.name or "Math"}

	def update_classroom(self, command: UpdateClassRoomCommand):
		if command.classroom_id != "1":
			raise ClassRoomNotFoundError("ClassRoom not found")
		return {"id": "1"}

	def delete_classroom(self, classroom_id: str):
		if classroom_id != "1":
			raise ClassRoomNotFoundError("ClassRoom not found")

	def update_enrollment(self, command: UpdateEnrollmentCommand):
		if command.enrollment_id != "1":
			raise EnrollmentNotFoundError("Enrollment not found")
		return {"id": "1"}


class AcademicsUseCaseTests(TestCase):
	def test_update_group_raises_not_found(self):
		use_case = UpdateGroupUseCase(repository=_InMemoryAcademicsRepository())

		with self.assertRaises(GroupNotFoundError):
			use_case.execute(UpdateGroupCommand(group_id="missing", letter="B"))

	def test_update_subject_raises_not_found(self):
		use_case = UpdateSubjectUseCase(repository=_InMemoryAcademicsRepository())

		with self.assertRaises(SubjectNotFoundError):
			use_case.execute(UpdateSubjectCommand(subject_id="missing", name="Science"))

	def test_update_classroom_raises_not_found(self):
		use_case = UpdateClassRoomUseCase(repository=_InMemoryAcademicsRepository())

		with self.assertRaises(ClassRoomNotFoundError):
			use_case.execute(UpdateClassRoomCommand(classroom_id="missing"))

	def test_delete_classroom_raises_not_found(self):
		use_case = DeleteClassRoomUseCase(repository=_InMemoryAcademicsRepository())

		with self.assertRaises(ClassRoomNotFoundError):
			use_case.execute("missing")

	def test_update_enrollment_raises_not_found(self):
		use_case = UpdateEnrollmentUseCase(repository=_InMemoryAcademicsRepository())

		with self.assertRaises(EnrollmentNotFoundError):
			use_case.execute(UpdateEnrollmentCommand(enrollment_id="missing"))


class AcademicsEndpointsSmokeTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.admin = Staff.objects.create_user(
			username="admin-academics-smoke",
			password="pass1234",
			role="Admin",
		)
		self.client.force_authenticate(user=self.admin)

		self.school_grade = SchoolGrade.objects.create(name="3ro")
		self.group = Group.objects.create(letter="A", school_grade=self.school_grade)
		self.subject = Subject.objects.create(name="History", school_grade=self.school_grade)
		self.class_room = ClassRoom.objects.create(group=self.group, staff=self.admin)
		self.student = Student.objects.create(
			first_name="Alicia",
			second_name="Mar",
			last_name="Vega",
			enrollment_number="E20261111",
			date_of_birth="2014-10-10",
			gender="F",
			state="active",
		)
		self.enrollment = Enrollment.objects.create(
			student=self.student,
			group=self.group,
			period="2026",
			state="active",
		)

	def test_update_group_endpoint_returns_200(self):
		response = self.client.put(
			f"/api/academics/groups/{self.group.id}/",
			{"letter": "B"},
			format="json",
		)

		self.assertEqual(response.status_code, 200)

	def test_update_subject_endpoint_returns_200(self):
		response = self.client.put(
			f"/api/academics/subjects/{self.subject.id}/",
			{"name": "History 2"},
			format="json",
		)

		self.assertEqual(response.status_code, 200)

	def test_update_classroom_endpoint_returns_200(self):
		response = self.client.put(
			f"/api/academics/classrooms/{self.class_room.id}/",
			{"group_id": str(self.group.id), "staff_id": str(self.admin.id)},
			format="json",
		)

		self.assertEqual(response.status_code, 200)

	def test_update_enrollment_endpoint_returns_200(self):
		response = self.client.put(
			f"/api/academics/enrollments/{self.enrollment.id}/",
			{"state": "inactive", "period": "2027"},
			format="json",
		)

		self.assertEqual(response.status_code, 200)


class AcademicsAuthorizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = Staff.objects.create_user(
            username="teacher-academics-auth",
            password="pass1234",
            role="Teacher",
        )
        self.other_teacher = Staff.objects.create_user(
            username="other-teacher-academics-auth",
            password="pass1234",
            role="Teacher",
        )
        self.school_grade = SchoolGrade.objects.create(name="5to-auth")
        self.own_group = Group.objects.create(letter="A", school_grade=self.school_grade)
        self.other_group = Group.objects.create(letter="B", school_grade=self.school_grade)
        self.own_classroom = ClassRoom.objects.create(
            group=self.own_group,
            staff=self.teacher,
        )
        self.other_classroom = ClassRoom.objects.create(
            group=self.other_group,
            staff=self.other_teacher,
        )
        self.subject = Subject.objects.create(
            name="Mathematics-auth",
            school_grade=self.school_grade,
        )

    def test_anonymous_user_cannot_list_classrooms(self):
        response = self.client.get("/api/academics/classrooms/")

        self.assertEqual(response.status_code, 401)

    def test_teacher_lists_only_assigned_classrooms(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get("/api/academics/classrooms/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.data], [str(self.own_classroom.id)])

    def test_teacher_cannot_read_another_classroom(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(
            f"/api/academics/classrooms/{self.other_classroom.id}/"
        )

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_create_classroom(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post(
            "/api/academics/classrooms/",
            {"group_id": str(self.own_group.id), "staff_id": str(self.teacher.id)},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_teacher_can_read_subjects_for_assigned_classroom(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(
            f"/api/academics/subjects/classroom/{self.own_classroom.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.data], [str(self.subject.id)])

    def test_teacher_cannot_read_subjects_for_another_classroom(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(
            f"/api/academics/subjects/classroom/{self.other_classroom.id}/"
        )

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_update_subject(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.patch(
            f"/api/academics/subjects/{self.subject.id}/",
            {"name": "Forbidden change"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
