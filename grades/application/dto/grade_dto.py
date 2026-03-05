from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CreateGradeCommand:
    student_id: str
    class_room_id: str
    type_code_id: str
    subject_id: str
    score: Decimal
    max_score: Decimal
    description: str | None
