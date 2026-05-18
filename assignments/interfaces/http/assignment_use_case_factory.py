from assignments.application.use_cases.assignments_use_cases import (
    CreateAssignmentUseCase,
    DeleteAssignmentUseCase,
    ListAssignmentsUseCase,
)

from assignments.application.use_cases.update_assigment import UpdateAssignmentUseCase
from assignments.infrastructure.repositories.django_assignment_repository import (
    DjangoAssignmentRepository,
)


def build_list_assignments_use_case() -> ListAssignmentsUseCase:
    return ListAssignmentsUseCase(repository=DjangoAssignmentRepository())

def build_create_assignment_use_case() -> CreateAssignmentUseCase:
    return CreateAssignmentUseCase(repository=DjangoAssignmentRepository())

def build_update_assignment_use_case() -> UpdateAssignmentUseCase:
    return UpdateAssignmentUseCase(repository=DjangoAssignmentRepository())

def build_delete_assignment_use_case() -> DeleteAssignmentUseCase:
    return DeleteAssignmentUseCase(repository=DjangoAssignmentRepository())