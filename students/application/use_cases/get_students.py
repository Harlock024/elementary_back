from students.domain.exceptions.student_exceptions import StudentNotFoundError
from students.domain.repositories.student_repository import StudentRepository


class ListStudentsUseCase:
    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def execute(self) -> list[dict]:
        return self.repository.list_students_detail()
    
class ListStudentsByGroupUseCase:
    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def execute(self, group_id: str) -> list[dict]:
        return self.repository.list_students_by_group(group_id)


class ListStudentsByClassroomUseCase:
    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def execute(self, classroom_id: str) -> list[dict]:
        return self.repository.list_students_by_classroom(classroom_id)


class GetStudentDetailUseCase:
    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def execute(self, student_id: str) -> dict:
        student = self.repository.get_student_detail(student_id)
        if student is None:
            raise StudentNotFoundError("Student not found")
        return student


class GetStudentProfileUseCase:
    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def execute(self, student_id: str) -> dict:
        student = self.repository.get_student_profile(student_id)
        if student is None:
            raise StudentNotFoundError("Student not found")
        return student
