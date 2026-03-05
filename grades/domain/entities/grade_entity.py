from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class GradeEntity:
    student_id: str
    class_room_id: str
    type_code_id: str
    subject_id: str
    score: Decimal
    max_score: Decimal

    def __post_init__(self):
        if not self.student_id:
            raise ValueError("student is required")
        if not self.class_room_id:
            raise ValueError("class_room is required")
        if not self.type_code_id:
            raise ValueError("type_code is required")
        if not self.subject_id:
            raise ValueError("subject is required")
        if self.max_score <= Decimal("0"):
            raise ValueError("max_score must be greater than zero")
