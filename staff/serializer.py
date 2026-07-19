from rest_framework import serializers

from .models import Staff


class StaffSerializer(serializers.ModelSerializer):
    """Public representation of a staff account; credentials are never exposed."""

    class Meta:
        model = Staff
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class StaffProfileUpdateSerializer(serializers.ModelSerializer):
    """Fields users may safely edit on their own account."""

    forbidden_fields = {
        "username",
        "role",
        "password",
        "is_active",
        "is_staff",
        "is_superuser",
        "user_permissions",
        "groups",
    }

    class Meta:
        model = Staff
        fields = ["first_name", "last_name", "email"]

    def to_internal_value(self, data):
        forbidden = sorted(self.forbidden_fields.intersection(data.keys()))
        if forbidden:
            raise serializers.ValidationError(
                {field: "This field cannot be changed from the profile endpoint." for field in forbidden}
            )
        return super().to_internal_value(data)

    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("First name cannot be blank.")
        return value.strip()

    def validate_last_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Last name cannot be blank.")
        return value.strip()

class StaffSerializerDetail(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id', 'username', 'first_name', 'last_name', 'role', 'created_at', 'updated_at']

class StaffSerializerNameOnly(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id', 'first_name',"username"]
