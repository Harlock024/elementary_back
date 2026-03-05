from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CreateAttendanceCommand:
    student_id: str
    state_code_id: str
    class_id: str
    attendance_date: date
