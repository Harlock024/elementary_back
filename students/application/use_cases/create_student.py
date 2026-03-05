from students.application.dto.student_dto import CreateStudentCommand
from students.domain.entities.student_entity import StudentEntity
from students.domain.repositories.student_repository import StudentRepository


class CreateStudentWithEnrollmentUseCase:
    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def execute(self, command: CreateStudentCommand) -> dict:
        StudentEntity(
            first_name=command.first_name,
            second_name=command.second_name,
            last_name=command.last_name,
            date_of_birth=command.date_of_birth,
            gender=command.gender,
            state=command.state,
        )
        return self.repository.create_student_with_enrollment(command)
