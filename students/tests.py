from datetime import date
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from academics.models import ClassRoom, Enrollment, Group, SchoolGrade, Subject
from assignments.models import Assignment
from grades.models import GradingCriteria, StudentGrade
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


class StudentAuthorizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = Staff.objects.create_user(
            username="teacher-students",
            password="test1234",
            role="Teacher",
        )
        self.other_teacher = Staff.objects.create_user(
            username="other-teacher-students",
            password="test1234",
            role="Teacher",
        )
        self.admin = Staff.objects.create_user(
            username="admin-students-auth",
            password="test1234",
            role="Admin",
        )
        school_grade = SchoolGrade.objects.create(name="4to-auth")
        self.own_group = Group.objects.create(letter="A", school_grade=school_grade)
        self.other_group = Group.objects.create(letter="B", school_grade=school_grade)
        self.own_classroom = ClassRoom.objects.create(
            group=self.own_group,
            staff=self.teacher,
        )
        self.other_classroom = ClassRoom.objects.create(
            group=self.other_group,
            staff=self.other_teacher,
        )
        self.own_student = self._create_student("E20269001", "Own", self.own_group)
        self.other_student = self._create_student("E20269002", "Other", self.other_group)

    def _create_student(self, enrollment_number, first_name, group):
        student = Student.objects.create(
            first_name=first_name,
            last_name="Student",
            curp=f"CURP{enrollment_number}",
            tutor_name="Tutor",
            tutor_phone="5550000000",
            tutor_relationship="Tutor",
            enrollment_number=enrollment_number,
            date_of_birth="2015-01-01",
            gender="X",
            state="activo",
        )
        Enrollment.objects.create(
            student=student,
            group=group,
            period="2026-2027",
            state="activo",
        )
        return student

    def _add_cross_class_history(self):
        historical_enrollment = Enrollment.objects.create(
            student=self.own_student,
            group=self.other_group,
            period="2025-2026",
            state="inactivo",
        )
        subject = Subject.objects.create(
            name="Profile subject",
            school_grade=self.own_group.school_grade,
        )
        own_criteria = GradingCriteria.objects.create(
            name="Own criteria",
            class_room=self.own_classroom,
            percentage=Decimal("50.00"),
        )
        other_criteria = GradingCriteria.objects.create(
            name="Other criteria",
            class_room=self.other_classroom,
            percentage=Decimal("50.00"),
        )
        own_assignment = Assignment.objects.create(
            class_room=self.own_classroom,
            subject=subject,
            grading_criteria=own_criteria,
            title="Own grade",
            due_date=date.today(),
            max_score=Decimal("10.00"),
        )
        other_assignment = Assignment.objects.create(
            class_room=self.other_classroom,
            subject=subject,
            grading_criteria=other_criteria,
            title="Foreign grade",
            due_date=date.today(),
            max_score=Decimal("10.00"),
        )
        own_grade = StudentGrade.objects.create(
            student=self.own_student,
            class_room=self.own_classroom,
            subject=subject,
            assignment=own_assignment,
            score=Decimal("9.00"),
            date=date.today(),
        )
        other_grade = StudentGrade.objects.create(
            student=self.own_student,
            class_room=self.other_classroom,
            subject=subject,
            assignment=other_assignment,
            score=Decimal("8.00"),
            date=date.today(),
        )
        own_enrollment = self.own_student.enrollments.get(
            group=self.own_group,
            state="activo",
        )
        return own_enrollment, historical_enrollment, own_grade, other_grade

    def test_anonymous_user_cannot_list_students(self):
        response = self.client.get("/api/students/")

        self.assertEqual(response.status_code, 401)

    def test_teacher_can_list_students_from_assigned_classroom(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(
            f"/api/students/?classroom_id={self.own_classroom.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.data], [str(self.own_student.id)])

    def test_teacher_cannot_list_students_from_another_classroom(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(
            f"/api/students/?classroom_id={self.other_classroom.id}"
        )

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_list_all_students(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get("/api/students/")

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_read_student_from_another_classroom(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(f"/api/students/{self.other_student.id}/")

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_create_student(self):
        self.client.force_authenticate(user=self.teacher)

        response = self.client.post("/api/students/", {}, format="json")

        self.assertEqual(response.status_code, 403)

    def test_teacher_detail_hides_enrollments_from_other_classrooms(self):
        own_enrollment, historical_enrollment, _, _ = self._add_cross_class_history()
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(f"/api/students/{self.own_student.id}/")

        self.assertEqual(response.status_code, 200)
        returned_ids = {item["id"] for item in response.data["enrollments"]}
        self.assertEqual(returned_ids, {str(own_enrollment.id)})
        self.assertNotIn(str(historical_enrollment.id), returned_ids)

    def test_admin_detail_keeps_complete_enrollment_history(self):
        own_enrollment, historical_enrollment, _, _ = self._add_cross_class_history()
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(f"/api/students/{self.own_student.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {item["id"] for item in response.data["enrollments"]},
            {str(own_enrollment.id), str(historical_enrollment.id)},
        )

    def test_teacher_profile_hides_grades_and_enrollments_from_other_classrooms(self):
        own_enrollment, historical_enrollment, own_grade, other_grade = (
            self._add_cross_class_history()
        )
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(
            f"/api/students/{self.own_student.id}/profile/"
        )

        self.assertEqual(response.status_code, 200)
        grade_ids = {str(item["id"]) for item in response.data["grades"]}
        enrollment_ids = {
            str(item["id"]) for item in response.data["enrollments"]
        }
        self.assertEqual(grade_ids, {str(own_grade.id)})
        self.assertNotIn(str(other_grade.id), grade_ids)
        self.assertEqual(enrollment_ids, {str(own_enrollment.id)})
        self.assertNotIn(str(historical_enrollment.id), enrollment_ids)

    def test_admin_profile_keeps_complete_grade_and_enrollment_history(self):
        own_enrollment, historical_enrollment, own_grade, other_grade = (
            self._add_cross_class_history()
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            f"/api/students/{self.own_student.id}/profile/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {str(item["id"]) for item in response.data["grades"]},
            {str(own_grade.id), str(other_grade.id)},
        )
        self.assertEqual(
            {str(item["id"]) for item in response.data["enrollments"]},
            {str(own_enrollment.id), str(historical_enrollment.id)},
        )
