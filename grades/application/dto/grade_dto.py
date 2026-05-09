from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class CreateGradeCommand:
    student_id: str
    class_room_id: str
    assignment_id: str
    subject_id: str
    score: Decimal
    date: date
    description: str | None


@dataclass(frozen=True)
class UpdateGradeCommand:
    grade_id: int
    score: Optional[Decimal] = None
    description: Optional[str] = None
