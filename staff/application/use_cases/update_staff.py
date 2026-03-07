from staff.application.dto.staff_dto import UpdateStaffCommand
from staff.domain.repositories.staff_repository import StaffRepository


class UpdateStaffUseCase:
    def __init__(self, repository: StaffRepository):
        self.repository = repository

    def execute(self, command: UpdateStaffCommand) -> dict:
        return self.repository.update_staff(command)
