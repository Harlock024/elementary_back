from students.domain.exceptions.student_exceptions import StudentNotFoundError
from students.domain.repositories.student_repository import StudentRepository


class ListStudentsUseCase:
    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def execute(self) -> list[dict]:
        return self.repository.list_students_detail()


class GetStudentDetailUseCase:
    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def execute(self, student_id: str) -> dict:
        student = self.repository.get_student_detail(student_id)
        if student is None:
            raise StudentNotFoundError("Student not found")
        return student
