import random
import string

from staff.application.dto.staff_dto import CreateStaffCommand
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
