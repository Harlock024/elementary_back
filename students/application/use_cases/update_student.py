from students.application.dto.student_dto import UpdateStudentCommand
from students.domain.repositories.student_repository import StudentRepository


class UpdateStudentUseCase:
    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def execute(self, command: UpdateStudentCommand) -> dict:
        return self.repository.update_student(command)
