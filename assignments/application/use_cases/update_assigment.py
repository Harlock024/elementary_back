from assignments.application.dtos.assignments_dto import UpdateAssignmentCommand
from assignments.domain.repositories import AssignmentRepository   

class UpdateAssignmentUseCase:
    def __init__(self, repository: AssignmentRepository):
        self.repository = repository

    def execute(self, command: UpdateAssignmentCommand) -> dict:
        return self.repository.update_assignment(command)