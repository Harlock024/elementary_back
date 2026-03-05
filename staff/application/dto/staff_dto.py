from dataclasses import dataclass


@dataclass(frozen=True)
class CreateStaffCommand:
    first_name: str
    last_name: str
