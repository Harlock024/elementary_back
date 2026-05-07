from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass(frozen=True)
class CreateAssignmentCommand:
    title: str
    description: str
    due_date: date
    class_id: str
    subject_id: str
    grading_criteria_id: str
    max_score: float


@dataclass(frozen=True)
class UpdateAssignmentCommand:
    assignment_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    class_id: Optional[str] = None
    subject_id: Optional[str] = None
    grading_criteria_id: Optional[str] = None
    max_score: Optional[float] = None

