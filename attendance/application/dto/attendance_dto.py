from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class CreateAttendanceCommand:
    id: str | None
    student_id: str
    state_code_id: str
    class_id: str
    attendance_date: date


@dataclass(frozen=True)
class UpdateAttendanceCommand:
    attendance_id: str
    version: int
    state_code_id: Optional[str] = None
