from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from staff.application.dto.staff_dto import CreateStaffCommand, UpdateStaffCommand
from staff.domain.exceptions.staff_exceptions import StaffNotFoundError
from staff.models import Staff
from staff.serializer import StaffSerializer

class DjangoStaffRepository:
    def list_staff(self) -> list[dict]:
        staffs = Staff.objects.all()
        return StaffSerializer(staffs, many=True).data

    def create_staff(self, command: CreateStaffCommand) -> dict:
        first_name = command.first_name.strip()
        last_name = command.last_name.strip()
        username = (
            command.username or f"{first_name.lower()}_{last_name.lower()}"
        ).strip()

        if Staff.objects.filter(username=username).exists():
            raise ValueError("username already exists")
        valid_roles = {value for value, _ in Staff.ROLE_CHOICES}
        if command.role not in valid_roles:
            raise ValueError("invalid role")

        staff = Staff(
            first_name=first_name,
            last_name=last_name,
            username=username,
            role=command.role,
        )
        try:
            validate_password(command.password, user=staff)
        except ValidationError as exc:
            raise ValueError(" ".join(exc.messages)) from exc

        staff.set_password(command.password)
        staff.save()

        return StaffSerializer(staff).data

    def update_staff(self, command: UpdateStaffCommand) -> dict:
        staff = Staff.objects.filter(pk=command.staff_id).first()
        if staff is None:
            raise StaffNotFoundError("Staff not found")

        if command.first_name is not None:
            staff.first_name = command.first_name
        if command.last_name is not None:
            staff.last_name = command.last_name
        if command.username is not None:
            if Staff.objects.exclude(pk=staff.pk).filter(username=command.username).exists():
                raise ValueError("username already exists")
            staff.username = command.username
        if command.role is not None:
            if command.role not in {"Admin", "Principal", "Teacher"}:
                raise ValueError("invalid role")
            staff.role = command.role

        staff.save()
        return StaffSerializer(staff).data

    def delete_staff(self, staff_id: str) -> None:
        staff = Staff.objects.filter(pk=staff_id).first()
        if staff is None:
            raise StaffNotFoundError("Staff not found")
        staff.delete()
