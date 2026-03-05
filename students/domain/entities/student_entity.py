from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class StudentEntity:
    first_name: str
    second_name: str | None
    last_name: str
    date_of_birth: date
    gender: str
    state: str

    def __post_init__(self):
        if not self.first_name or not self.first_name.strip():
            raise ValueError("first_name is required")
        if not self.last_name or not self.last_name.strip():
            raise ValueError("last_name is required")
        if not self.gender or not self.gender.strip():
            raise ValueError("gender is required")
        if not self.state or not self.state.strip():
            raise ValueError("state is required")
