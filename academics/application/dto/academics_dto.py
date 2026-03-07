from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UpdateGroupCommand:
    group_id: str
    letter: Optional[str] = None
    school_grade_id: Optional[str] = None


@dataclass(frozen=True)
class UpdateSubjectCommand:
    subject_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    school_grade_id: Optional[str] = None


@dataclass(frozen=True)
class UpdateClassRoomCommand:
    classroom_id: str
    group_id: Optional[str] = None
    staff_id: Optional[str] = None


@dataclass(frozen=True)
class UpdateEnrollmentCommand:
    enrollment_id: str
    student_id: Optional[str] = None
    group_id: Optional[str] = None
    period: Optional[str] = None
    state: Optional[str] = None
