from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CreateStudentCommand:
    first_name: str
    second_name: str | None
    last_name: str
    date_of_birth: date
    gender: str
    state: str
    group_id: str
    period: str
