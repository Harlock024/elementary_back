from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class GradeEntity:
    student_id: str
    class_room_id: str
    assignment_id: str
    subject_id: str
    score: Decimal

    def __post_init__(self):
        if not self.student_id:
            raise ValueError("student is required")
        if not self.class_room_id:
            raise ValueError("class_room is required")
        if not self.assignment_id:
            raise ValueError("assignment is required")
        if not self.subject_id:
            raise ValueError("subject is required")
        if self.score < Decimal("0"):
            raise ValueError("score must be zero or greater")
