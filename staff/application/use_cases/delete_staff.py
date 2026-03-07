from staff.domain.repositories.staff_repository import StaffRepository


class DeleteStaffUseCase:
    def __init__(self, repository: StaffRepository):
        self.repository = repository

    def execute(self, staff_id: str) -> None:
        self.repository.delete_staff(staff_id)
