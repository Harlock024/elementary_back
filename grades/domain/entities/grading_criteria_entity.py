from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class GradingCriteriaEntity:
    grading_criteria_id: str
    name: str
    class_room_id: str
    subject_id: str
    percentage: Decimal

    def __post_init__(self):
        if not self.grading_criteria_id:
            raise ValueError("grading_criteria_id is required")
        if not self.name:
            raise ValueError("name is required")
        if not self.class_room_id:
            raise ValueError("class_room_id is required")
        if not self.subject_id:
            raise ValueError("subject_id is required")
        if self.percentage <= Decimal("0") or self.percentage > Decimal("100"):
            raise ValueError("percentage must be greater than zero and less than or equal to 100")