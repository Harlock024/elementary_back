from assignments.application.dtos.assignments_dto import CreateAssignmentCommand
from assignments.domain.entities.assignment_entity import AssignmentEntity
from assignments.domain.repositories import AssignmentRepository


class ListAssignmentsUseCase:
    def __init__(self, repository: AssignmentRepository):
        self.repository = repository

    def execute(
        self,
        class_id: str | None = None,
        student_id: str | None = None,
    ) -> list[dict]:
        return self.repository.list_assignments(
            class_id=class_id,
            student_id=student_id,
        )


class CreateAssignmentUseCase:
    def __init__(self, repository: AssignmentRepository):
        self.repository = repository

    def execute(self, command: CreateAssignmentCommand) -> dict:
        AssignmentEntity(
            class_id=command.class_id,
            subject_id=command.subject_id,
            grading_criteria_id=command.grading_criteria_id,
            title=command.title,
            description=command.description,
            due_date=command.due_date,
            max_score=command.max_score,
        )
        return self.repository.create_assignment(command)


class DeleteAssignmentUseCase:
    def __init__(self, repository: AssignmentRepository):
        self.repository = repository

    def execute(self, assignment_id: str) -> None:
        self.repository.delete_assignment(assignment_id)
