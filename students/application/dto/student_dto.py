from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class CreateStudentCommand:
    first_name: str
    second_name: str | None
    last_name: str
    curp: str
    tutor_name: str
    tutor_phone: str
    tutor_relationship: str
    date_of_birth: date
    gender: str
    state: str
    group_id: str
    period: str
    academic_period_id: Optional[str] = None


@dataclass(frozen=True)
class UpdateStudentCommand:
    student_id: str
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    last_name: Optional[str] = None
    curp: Optional[str] = None
    tutor_name: Optional[str] = None
    tutor_phone: Optional[str] = None
    tutor_relationship: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    group_id: Optional[str] = None
    period: Optional[str] = None
    academic_period_id: Optional[str] = None
