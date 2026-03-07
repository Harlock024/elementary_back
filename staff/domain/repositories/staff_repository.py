from typing import Protocol

from staff.application.dto.staff_dto import CreateStaffCommand, UpdateStaffCommand


class StaffRepository(Protocol):
    def list_staff(self) -> list[dict]:
        ...

    def create_staff(self, command: CreateStaffCommand) -> dict:
        ...

    def update_staff(self, command: UpdateStaffCommand) -> dict:
        ...

    def delete_staff(self, staff_id: str) -> None:
        ...
