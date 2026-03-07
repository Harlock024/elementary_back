from students.domain.repositories.student_repository import StudentRepository


class DeleteStudentUseCase:
    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def execute(self, student_id: str) -> None:
        self.repository.delete_student(student_id)
