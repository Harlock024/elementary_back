from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class CreateGradingCriteriaCommand:
    name: str
    class_room_id: str
    percentage: Decimal
    is_attendance_based: bool = False


@dataclass(frozen=True)
class UpdateGradingCriteriaCommand:
    grading_criteria_id: str
    name: Optional[str] = None
    class_room_id: Optional[str] = None
    percentage: Optional[Decimal] = None
    is_attendance_based: Optional[bool] = None
