from students.application.use_cases.create_student import CreateStudentWithEnrollmentUseCase
from students.application.use_cases.get_students import (
    GetStudentDetailUseCase,
    ListStudentsUseCase,
)
from students.infrastructure.repositories.django_student_repository import DjangoStudentRepository


def build_list_students_use_case() -> ListStudentsUseCase:
    return ListStudentsUseCase(repository=DjangoStudentRepository())


def build_get_student_detail_use_case() -> GetStudentDetailUseCase:
    return GetStudentDetailUseCase(repository=DjangoStudentRepository())


def build_create_student_use_case() -> CreateStudentWithEnrollmentUseCase:
    return CreateStudentWithEnrollmentUseCase(repository=DjangoStudentRepository())
