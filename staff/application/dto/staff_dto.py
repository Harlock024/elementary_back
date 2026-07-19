from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateStaffCommand:
    first_name: str
    last_name: str
    password: str
    username: Optional[str] = None
    role: str = "Teacher"


@dataclass(frozen=True)
class UpdateStaffCommand:
    staff_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
