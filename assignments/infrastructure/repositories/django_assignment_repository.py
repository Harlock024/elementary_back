from academics.models import ClassRoom
from assignments.application.dtos.assignments_dto import CreateAssignmentCommand, UpdateAssignmentCommand
from assignments.domain.exceptions.assignments_exception import (
    AssignmentsAlreadyExistsError,
    AssignmentsNotFoundError,
    ClassRoomNotFoundError,
)
from assignments.models import Assignment
from grades.models import GradingCriteria


class DjangoAssignmentRepository:
    def list_assignments(
        self,
        class_id: str | None = None,
        student_id: str | None = None,
    ) -> list[dict]:
        qs = Assignment.objects.select_related("class_room", "subject", "grading_criteria")
        if class_id:
            qs = qs.filter(class_room_id=class_id)
        if student_id:
            qs = qs.filter(class_room__group__enrollments__student_id=student_id).distinct()
        return [self._to_dict(a) for a in qs]

    def create_assignment(self, command: CreateAssignmentCommand) -> dict:
        if not ClassRoom.objects.filter(pk=command.class_id).exists():
            raise ClassRoomNotFoundError("ClassRoom not found")
        if not GradingCriteria.objects.filter(pk=command.grading_criteria_id).exists():
            raise AssignmentsAlreadyExistsError("GradingCriteria not found")

        assignment = Assignment.objects.create(
            class_room_id=command.class_id,
            subject_id=command.subject_id,
            grading_criteria_id=command.grading_criteria_id,
            title=command.title,
            description=command.description,
            due_date=command.due_date,
            max_score=command.max_score,
        )
        return self._to_dict(assignment)

    def update_assignment(self, command: UpdateAssignmentCommand) -> dict:
        assignment = Assignment.objects.filter(pk=command.assignment_id).first()
        if assignment is None:
            raise AssignmentsNotFoundError("Assignment not found")

        if command.title is not None:
            assignment.title = command.title
        if command.description is not None:
            assignment.description = command.description
        if command.due_date is not None:
            assignment.due_date = command.due_date
        if command.max_score is not None:
            assignment.max_score = command.max_score
        if command.subject_id is not None:
            assignment.subject_id = command.subject_id
        if command.grading_criteria_id is not None:
            assignment.grading_criteria_id = command.grading_criteria_id

        assignment.save()
        return self._to_dict(assignment)

    def delete_assignment(self, assignment_id: str) -> None:
        assignment = Assignment.objects.filter(pk=assignment_id).first()
        if assignment is None:
            raise AssignmentsNotFoundError("Assignment not found")
        assignment.delete()

    def _to_dict(self, assignment: Assignment) -> dict:
        return {
            "id": str(assignment.id),
            "class_room_id": str(assignment.class_room_id),
            "subject_id": str(assignment.subject_id),
            "grading_criteria_id": str(assignment.grading_criteria_id),
            "title": assignment.title,
            "description": assignment.description,
            "due_date": str(assignment.due_date),
            "max_score": float(assignment.max_score),
            "created_at": assignment.created_at.isoformat(),
            "updated_at": assignment.updated_at.isoformat(),
        }
