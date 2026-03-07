from academics.application.dto.school_grade_dto import CreateSchoolGradeCommand, UpdateSchoolGradeCommand
from academics.domain.exceptions.school_grade_exceptions import SchoolGradeNotFoundError
from academics.models import SchoolGrade
from academics.serializer import SchoolGradeSerializer


class DjangoSchoolGradeRepository:
    def list_school_grades(self) -> list[dict]:
        school_grades = SchoolGrade.objects.all()
        return SchoolGradeSerializer(school_grades, many=True).data

    def get_school_grade(self, school_grade_id: str) -> dict | None:
        school_grade = SchoolGrade.objects.filter(pk=school_grade_id).first()
        if school_grade is None:
            return None
        return SchoolGradeSerializer(school_grade).data

    def create_school_grade(self, command: CreateSchoolGradeCommand) -> dict:
        school_grade = SchoolGrade(name=command.name)
        school_grade.save()
        return SchoolGradeSerializer(school_grade).data

    def update_school_grade(self, command: UpdateSchoolGradeCommand) -> dict:
        school_grade = SchoolGrade.objects.filter(pk=command.school_grade_id).first()
        if school_grade is None:
            raise SchoolGradeNotFoundError("School Grade not found")

        if command.name is not None:
            school_grade.name = command.name

        school_grade.save()
        return SchoolGradeSerializer(school_grade).data
