from typing import Protocol

from staff.application.dto.staff_dto import CreateStaffCommand


class StaffRepository(Protocol):
    def list_staff(self) -> list[dict]:
        ...

    def create_staff(self, command: CreateStaffCommand) -> dict:
        ...
