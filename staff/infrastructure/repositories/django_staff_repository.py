import random
import string

from staff.application.dto.staff_dto import CreateStaffCommand, UpdateStaffCommand
from staff.domain.exceptions.staff_exceptions import StaffNotFoundError
from staff.models import Staff
from staff.serializer import StaffSerializer


def generate_random_password(length: int = 10) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(characters) for _ in range(length))


class DjangoStaffRepository:
    def list_staff(self) -> list[dict]:
        staffs = Staff.objects.all()
        return StaffSerializer(staffs, many=True).data

    def create_staff(self, command: CreateStaffCommand) -> dict:
        profesor = Staff(
            first_name=command.first_name,
            last_name=command.last_name,
            username=f"{command.first_name.lower()}_{command.last_name.lower()}",
        )

        random_password = generate_random_password()
        profesor.password_professor = random_password
        profesor.set_password(random_password)
        profesor.save()

        return StaffSerializer(profesor).data

    def update_staff(self, command: UpdateStaffCommand) -> dict:
        staff = Staff.objects.filter(pk=command.staff_id).first()
        if staff is None:
            raise StaffNotFoundError("Staff not found")

        if command.first_name is not None:
            staff.first_name = command.first_name
        if command.last_name is not None:
            staff.last_name = command.last_name
        if command.username is not None:
            staff.username = command.username
        if command.role is not None:
            staff.role = command.role

        staff.save()
        return StaffSerializer(staff).data

    def delete_staff(self, staff_id: str) -> None:
        staff = Staff.objects.filter(pk=staff_id).first()
        if staff is None:
            raise StaffNotFoundError("Staff not found")
        staff.delete()
