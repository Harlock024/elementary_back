from grades.application.use_cases.grade_use_cases import (
    CreateGradeUseCase,
    GetGradeUseCase,
    ListGradesUseCase,
)
from grades.infrastructure.repositories.django_grade_repository import DjangoGradeRepository


def build_list_grades_use_case() -> ListGradesUseCase:
    return ListGradesUseCase(repository=DjangoGradeRepository())


def build_get_grade_use_case() -> GetGradeUseCase:
    return GetGradeUseCase(repository=DjangoGradeRepository())


def build_create_grade_use_case() -> CreateGradeUseCase:
    return CreateGradeUseCase(repository=DjangoGradeRepository())
