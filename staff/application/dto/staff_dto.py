from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CreateStaffCommand:
    id: str | None
    first_name: str
    last_name: str


@dataclass(frozen=True)
class UpdateStaffCommand:
    staff_id: str
    version: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None
