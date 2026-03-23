from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class CreateGradeCommand:
    id: str | None
    student_id: str
    class_room_id: str
    type_code_id: str
    subject_id: str
    score: Decimal
    max_score: Decimal
    description: str | None


@dataclass(frozen=True)
class UpdateGradeCommand:
    grade_id: str
    version: int
    score: Optional[Decimal] = None
    max_score: Optional[Decimal] = None
    description: Optional[str] = None
    type_code_id: Optional[str] = None
