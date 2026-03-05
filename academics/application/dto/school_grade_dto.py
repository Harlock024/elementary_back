from dataclasses import dataclass


@dataclass(frozen=True)
class CreateSchoolGradeCommand:
    name: str
