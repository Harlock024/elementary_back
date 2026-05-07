from assignments.application.dtos.assignments_dto import CreateAssignmentCommand, UpdateAssignmentCommand       
from assignments.domain.exceptions import (
    AssigmentsAlreadyExistsException,
    AssigmentsNotFoundException,
    StudentNotFoundForAssignmentsError,
    ClassRoomNotFoundError
)