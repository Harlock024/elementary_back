from dataclasses import dataclass


@dataclass(frozen=True)
class SchoolGradeEntity:
    name: str

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("name is required")
