from academics.application.use_cases.school_grade_use_cases import (
    CreateSchoolGradeUseCase,
    GetSchoolGradeUseCase,
    ListSchoolGradesUseCase,
)
from academics.application.use_cases.update_school_grade import UpdateSchoolGradeUseCase
from academics.infrastructure.repositories.django_school_grade_repository import (
    DjangoSchoolGradeRepository,
)


def build_list_school_grades_use_case() -> ListSchoolGradesUseCase:
    return ListSchoolGradesUseCase(repository=DjangoSchoolGradeRepository())


def build_get_school_grade_use_case() -> GetSchoolGradeUseCase:
    return GetSchoolGradeUseCase(repository=DjangoSchoolGradeRepository())


def build_create_school_grade_use_case() -> CreateSchoolGradeUseCase:
    return CreateSchoolGradeUseCase(repository=DjangoSchoolGradeRepository())


def build_update_school_grade_use_case() -> UpdateSchoolGradeUseCase:
    return UpdateSchoolGradeUseCase(repository=DjangoSchoolGradeRepository())
