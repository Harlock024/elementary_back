from staff.application.use_cases.staff_use_cases import (
    CreateStaffUseCase,
    ListStaffUseCase,
)
from staff.infrastructure.repositories.django_staff_repository import DjangoStaffRepository


def build_list_staff_use_case() -> ListStaffUseCase:
    return ListStaffUseCase(repository=DjangoStaffRepository())


def build_create_staff_use_case() -> CreateStaffUseCase:
    return CreateStaffUseCase(repository=DjangoStaffRepository())
