from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class AttendanceEntity:
    student_id: str
    state_code_id: str
    class_id: str
    attendance_date: date

    def __post_init__(self):
        if not self.student_id:
            raise ValueError("student_id is required")
        if not self.state_code_id:
            raise ValueError("state_code is required")
        if not self.class_id:
            raise ValueError("class_id is required")
