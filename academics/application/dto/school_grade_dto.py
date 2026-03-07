from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateSchoolGradeCommand:
    name: str


@dataclass(frozen=True)
class UpdateSchoolGradeCommand:
    school_grade_id: str
    name: Optional[str] = None
