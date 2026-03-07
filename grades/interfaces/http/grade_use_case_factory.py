from grades.application.use_cases.grade_use_cases import (
    CreateGradeUseCase,
    GetGradeUseCase,
    ListGradesUseCase,
)
from grades.application.use_cases.delete_grade import DeleteGradeUseCase
from grades.application.use_cases.update_grade import UpdateGradeUseCase
from grades.infrastructure.repositories.django_grade_repository import DjangoGradeRepository


def build_list_grades_use_case() -> ListGradesUseCase:
    return ListGradesUseCase(repository=DjangoGradeRepository())


def build_get_grade_use_case() -> GetGradeUseCase:
    return GetGradeUseCase(repository=DjangoGradeRepository())


def build_create_grade_use_case() -> CreateGradeUseCase:
    return CreateGradeUseCase(repository=DjangoGradeRepository())


def build_update_grade_use_case() -> UpdateGradeUseCase:
    return UpdateGradeUseCase(repository=DjangoGradeRepository())


def build_delete_grade_use_case() -> DeleteGradeUseCase:
    return DeleteGradeUseCase(repository=DjangoGradeRepository())
