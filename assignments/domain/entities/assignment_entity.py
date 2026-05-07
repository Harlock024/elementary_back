from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class AssignmentEntity:
    title: str
    description: str
    due_date: date
    class_id: str
    max_score: float
    subject_id: str
    grading_criteria_id: str

    def __post_init__(self):
        if not self.title:
            raise ValueError("title is required")
        if not self.due_date:
            raise ValueError("due_date is required")
        if not self.class_id:
            raise ValueError("class_id is required")
        if not self.max_score:
            raise ValueError("max_score is required")
        if not self.subject_id:
            raise ValueError("subject_id is required")
        if not self.grading_criteria_id:
            raise ValueError("grading_criteria_id is required")
    