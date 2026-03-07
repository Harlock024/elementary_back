from grades.domain.repositories.grade_repository import GradeRepository


class DeleteGradeUseCase:
    def __init__(self, repository: GradeRepository):
        self.repository = repository

    def execute(self, grade_id: int) -> None:
        self.repository.delete_grade(grade_id)
