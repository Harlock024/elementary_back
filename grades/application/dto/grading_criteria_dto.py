from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class CreateGradingCriteriaCommand:
    name: str
    class_room_id: str
    subject_id: str
    percentage: Decimal

@dataclass(frozen=True)
class UpdateGradingCriteriaCommand:
    grading_criteria_id: str
    name: Optional[str] = None
    class_room_id: Optional[str] = None
    subject_id: Optional[str] = None
    percentage: Optional[Decimal] = None