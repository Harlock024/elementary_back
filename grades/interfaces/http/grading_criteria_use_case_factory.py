from grades.application.use_cases.grading_criteria_use_case import (
    CreateGradingCriteriaUseCase,
    DeleteGradingCriteriaUseCase,
    GetGradingCriteriaUseCase,
    ListGradingCriteriaUseCase,
    UpdateGradingCriteriaUseCase,   
)

from grades.infrastructure.repositories.django_grading_criteria_repository import DjangoGradingCriteriaRepository


def build_list_grading_criteria_use_case() -> ListGradingCriteriaUseCase:
    return ListGradingCriteriaUseCase(repository=DjangoGradingCriteriaRepository())

def build_get_grading_criteria_use_case() -> GetGradingCriteriaUseCase:
    return GetGradingCriteriaUseCase(repository=DjangoGradingCriteriaRepository())

def build_create_grading_criteria_use_case() -> CreateGradingCriteriaUseCase:
    return CreateGradingCriteriaUseCase(repository=DjangoGradingCriteriaRepository())

def build_update_grading_criteria_use_case() -> UpdateGradingCriteriaUseCase:
    return UpdateGradingCriteriaUseCase(repository=DjangoGradingCriteriaRepository())

def build_delete_grading_criteria_use_case() -> DeleteGradingCriteriaUseCase:
    return DeleteGradingCriteriaUseCase(repository=DjangoGradingCriteriaRepository())

