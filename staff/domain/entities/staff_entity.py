from dataclasses import dataclass


@dataclass(frozen=True)
class StaffEntity:
    first_name: str
    last_name: str
    username: str

    def __post_init__(self):
        if not self.first_name or not self.first_name.strip():
            raise ValueError("first_name is required")
        if not self.last_name or not self.last_name.strip():
            raise ValueError("last_name is required")
        if not self.username or not self.username.strip():
            raise ValueError("username is required")
