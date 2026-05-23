from academics.application.use_cases.execute_promotion import ExecutePromotionUseCase
from academics.application.use_cases.academics_use_cases import (
    DeleteClassRoomUseCase,
    UpdateClassRoomUseCase,
    UpdateEnrollmentUseCase,
    UpdateGroupUseCase,
    DeleteGroupUseCase,
    UpdateSubjectUseCase,
    DeleteSubjectUseCase,
    DeleteEnrollmentUseCase,
)
from academics.infrastructure.repositories.django_academics_repository import (
    DjangoClassRoomRepository,
    DjangoEnrollmentRepository,
    DjangoGroupRepository,
    DjangoSubjectRepository,
)


def build_update_group_use_case() -> UpdateGroupUseCase:
    return UpdateGroupUseCase(repository=DjangoGroupRepository())

def build_delete_group_use_case() -> DeleteGroupUseCase:
    return DeleteGroupUseCase(repository=DjangoGroupRepository())


def build_update_subject_use_case() -> UpdateSubjectUseCase:
    return UpdateSubjectUseCase(repository=DjangoSubjectRepository())

def build_delete_subject_use_case() -> DeleteSubjectUseCase:
    return DeleteSubjectUseCase(repository=DjangoSubjectRepository())

def build_update_classroom_use_case() -> UpdateClassRoomUseCase:
    return UpdateClassRoomUseCase(repository=DjangoClassRoomRepository())


def build_delete_classroom_use_case() -> DeleteClassRoomUseCase:
    return DeleteClassRoomUseCase(repository=DjangoClassRoomRepository())


def build_list_enrollments_use_case() -> UpdateEnrollmentUseCase:
    return UpdateEnrollmentUseCase(repository=DjangoEnrollmentRepository())



def build_update_enrollment_use_case() -> UpdateEnrollmentUseCase:
    return UpdateEnrollmentUseCase(repository=DjangoEnrollmentRepository())

def build_delete_enrollment_use_case() -> DeleteEnrollmentUseCase:
    return DeleteEnrollmentUseCase(repository=DjangoEnrollmentRepository())


def build_execute_promotion_use_case() -> ExecutePromotionUseCase:
    return ExecutePromotionUseCase()
