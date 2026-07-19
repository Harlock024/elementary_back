import os
from pathlib import Path
import runpy
from unittest.mock import patch

from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.test import APIClient

from staff.application.dto.staff_dto import CreateStaffCommand
from staff.application.use_cases.delete_staff import DeleteStaffUseCase
from staff.application.use_cases.staff_use_cases import CreateStaffUseCase
from staff.application.use_cases.update_staff import UpdateStaffUseCase
from staff.domain.exceptions.staff_exceptions import StaffNotFoundError
from staff.models import Staff


PASSWORD = "SecurePass!2026"


class ProductionSettingsTests(SimpleTestCase):
    def test_missing_debug_configuration_fails_closed(self):
        settings_path = (
            Path(__file__).resolve().parents[1] / "elementary_back" / "settings.py"
        )

        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(Path, "is_file", return_value=False),
            self.assertRaises(ImproperlyConfigured),
        ):
            runpy.run_path(str(settings_path))


class _InMemoryStaffRepository:
    def list_staff(self):
        return [{"id": "1", "first_name": "Ana", "last_name": "Lopez"}]

    def create_staff(self, command: CreateStaffCommand):
        return {
            "id": "new",
            "first_name": command.first_name,
            "last_name": command.last_name,
        }

    def update_staff(self, command):
        if command.staff_id != "1":
            raise StaffNotFoundError("Staff not found")
        return {
            "id": "1",
            "first_name": command.first_name or "Ana",
            "last_name": command.last_name or "Lopez",
        }

    def delete_staff(self, staff_id: str):
        if staff_id != "1":
            raise StaffNotFoundError("Staff not found")


class StaffUseCaseTests(TestCase):
    def test_create_staff_validates_required_fields(self):
        use_case = CreateStaffUseCase(repository=_InMemoryStaffRepository())
        command = CreateStaffCommand(
            first_name="", last_name="Ramos", password=PASSWORD
        )

        with self.assertRaises(ValueError):
            use_case.execute(command)

    def test_create_staff_requires_password(self):
        use_case = CreateStaffUseCase(repository=_InMemoryStaffRepository())
        command = CreateStaffCommand(
            first_name="Ana", last_name="Ramos", password=""
        )

        with self.assertRaises(ValueError):
            use_case.execute(command)

    def test_update_staff_raises_not_found(self):
        use_case = UpdateStaffUseCase(repository=_InMemoryStaffRepository())

        with self.assertRaises(StaffNotFoundError):
            use_case.execute(
                type(
                    "Cmd",
                    (),
                    {
                        "staff_id": "missing",
                        "first_name": "A",
                        "last_name": None,
                        "username": None,
                        "role": None,
                    },
                )()
            )

    def test_delete_staff_raises_not_found(self):
        use_case = DeleteStaffUseCase(repository=_InMemoryStaffRepository())

        with self.assertRaises(StaffNotFoundError):
            use_case.execute("missing")


class StaffEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = Staff.objects.create_user(
            username="admin-user",
            password=PASSWORD,
            first_name="Ada",
            last_name="Admin",
            role="Admin",
        )
        self.client.force_authenticate(self.admin)

    def test_admin_can_create_staff_without_exposing_password(self):
        payload = {
            "first_name": "Carlos",
            "last_name": "Perez",
            "username": "carlos.perez",
            "role": "Teacher",
            "password": "TeacherPass!2026",
        }

        response = self.client.post("/api/staff/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["first_name"], payload["first_name"])
        self.assertNotIn("password", response.data)
        self.assertNotIn("password_professor", response.data)
        created = Staff.objects.get(username="carlos.perez")
        self.assertTrue(created.check_password(payload["password"]))

    def test_admin_cannot_create_staff_with_an_unknown_role(self):
        response = self.client.post(
            "/api/staff/",
            {
                "first_name": "Invalid",
                "last_name": "Role",
                "username": "invalid.role",
                "role": "Superuser",
                "password": "TeacherPass!2026",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Staff.objects.filter(username="invalid.role").exists())

    def test_admin_can_list_staff_without_credentials(self):
        response = self.client.get("/api/staff/")

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)
        self.assertTrue(
            all("password" not in item for item in response.data)
        )
        self.assertTrue(
            all("password_professor" not in item for item in response.data)
        )

    def test_admin_can_update_another_staff_member(self):
        staff = Staff.objects.create_user(
            username="staff-update-user",
            password=PASSWORD,
            first_name="Erika",
            last_name="Ramos",
        )

        response = self.client.put(
            f"/api/staff/{staff.id}/",
            {"first_name": "Erika2", "last_name": "Ramos"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["first_name"], "Erika2")

    def test_admin_can_delete_another_staff_member(self):
        staff = Staff.objects.create_user(
            username="staff-delete-user",
            password=PASSWORD,
            first_name="Marco",
            last_name="Paz",
        )

        response = self.client.delete(f"/api/staff/{staff.id}/")

        self.assertEqual(response.status_code, 204)

    def test_admin_cannot_change_own_role_or_username_through_admin_endpoint(self):
        response = self.client.put(
            f"/api/staff/{self.admin.id}/",
            {"username": "new-admin", "role": "Teacher"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.username, "admin-user")
        self.assertEqual(self.admin.role, "Admin")

    def test_admin_cannot_delete_own_account(self):
        response = self.client.delete(f"/api/staff/{self.admin.id}/")

        self.assertEqual(response.status_code, 400)
        self.assertTrue(Staff.objects.filter(pk=self.admin.pk).exists())


class StaffAuthorizationNegativeTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = Staff.objects.create_user(
            username="teacher-user",
            password=PASSWORD,
            first_name="Tania",
            last_name="Teacher",
            role="Teacher",
        )
        self.target = Staff.objects.create_user(
            username="target-user",
            password=PASSWORD,
            first_name="Target",
            last_name="User",
            role="Teacher",
        )

    def test_anonymous_user_cannot_access_staff_or_profile(self):
        requests = [
            ("get", "/api/staff/", None),
            ("post", "/api/staff/", {}),
            ("get", "/api/staff/profile/", None),
            ("post", "/api/staff/profile/change-password/", {}),
            ("post", "/api/staff/logout/", {"refresh": "invalid"}),
        ]

        for method, path, payload in requests:
            with self.subTest(method=method, path=path):
                response = getattr(self.client, method)(path, payload, format="json")
                self.assertEqual(response.status_code, 401)

    def test_teacher_cannot_manage_staff_or_use_legacy_admin_views(self):
        self.client.force_authenticate(self.teacher)
        requests = [
            ("get", "/api/staff/", None),
            (
                "post",
                "/api/staff/",
                {
                    "first_name": "Blocked",
                    "last_name": "Create",
                    "password": PASSWORD,
                },
            ),
            (
                "put",
                f"/api/staff/{self.target.id}/",
                {"first_name": "Blocked"},
            ),
            ("delete", f"/api/staff/{self.target.id}/", None),
            ("get", "/api/staff/professors/", None),
            (
                "post",
                "/api/staff/professors/create/",
                {
                    "first_name": "Blocked",
                    "last_name": "Legacy",
                    "password": PASSWORD,
                },
            ),
            (
                "patch",
                f"/api/staff/professors/{self.target.id}/",
                {"first_name": "Blocked"},
            ),
            ("delete", f"/api/staff/professors/{self.target.id}/delete/", None),
            (
                "post",
                "/api/staff/admin/",
                {
                    "first_name": "Blocked",
                    "last_name": "Admin",
                    "password": PASSWORD,
                },
            ),
        ]

        for method, path, payload in requests:
            with self.subTest(method=method, path=path):
                response = getattr(self.client, method)(path, payload, format="json")
                self.assertEqual(response.status_code, 403)

    def test_user_cannot_change_own_credentials_or_role_from_profile(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.patch(
            "/api/staff/profile/",
            {
                "username": "hacked-user",
                "role": "Admin",
                "password": "HackedPass!2026",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.teacher.refresh_from_db()
        self.assertEqual(self.teacher.username, "teacher-user")
        self.assertEqual(self.teacher.role, "Teacher")
        self.assertTrue(self.teacher.check_password(PASSWORD))

    def test_authenticated_user_can_only_update_safe_profile_fields(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.patch(
            "/api/staff/profile/",
            {"first_name": "Updated", "email": "updated@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.teacher.refresh_from_db()
        self.assertEqual(self.teacher.first_name, "Updated")
        self.assertEqual(self.teacher.email, "updated@example.com")


class StaffJwtTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = Staff.objects.create_user(
            username="jwt-user",
            password=PASSWORD,
            first_name="Julia",
            last_name="Web",
            role="Teacher",
        )

    def _login(self):
        return self.client.post(
            "/api/staff/login/",
            {"username": self.user.username, "password": PASSWORD},
            format="json",
        )

    def test_login_is_public_and_does_not_expose_passwords(self):
        response = self._login()

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertNotIn("password", response.data)
        self.assertNotIn("password_professor", response.data)

    @override_settings(JWT_LOGIN_RATE="2/min")
    def test_login_is_throttled_by_ip(self):
        cache.clear()
        payload = {"username": self.user.username, "password": "wrong-password"}

        first = self.client.post("/api/staff/login/", payload, format="json")
        second = self.client.post("/api/staff/login/", payload, format="json")
        throttled = self.client.post("/api/staff/login/", payload, format="json")

        self.assertEqual(first.status_code, 401)
        self.assertEqual(second.status_code, 401)
        self.assertEqual(throttled.status_code, 429)

    def test_refresh_route_rotates_and_blacklists_refresh_token(self):
        login = self._login()
        old_refresh = login.data["refresh"]

        refreshed = self.client.post(
            "/api/token/refresh/", {"refresh": old_refresh}, format="json"
        )

        self.assertEqual(refreshed.status_code, 200)
        self.assertIn("access", refreshed.data)
        self.assertIn("refresh", refreshed.data)
        self.assertNotEqual(refreshed.data["refresh"], old_refresh)

        reused = self.client.post(
            "/api/token/refresh/", {"refresh": old_refresh}, format="json"
        )
        self.assertEqual(reused.status_code, 401)

    def test_logout_requires_auth_and_revokes_refresh_token(self):
        login = self._login()
        access = login.data["access"]
        refresh = login.data["refresh"]

        unauthenticated = self.client.post(
            "/api/staff/logout/", {"refresh": refresh}, format="json"
        )
        self.assertEqual(unauthenticated.status_code, 401)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        logout = self.client.post(
            "/api/staff/logout/", {"refresh": refresh}, format="json"
        )
        self.assertEqual(logout.status_code, 204)

        self.client.credentials()
        reused = self.client.post(
            "/api/token/refresh/", {"refresh": refresh}, format="json"
        )
        self.assertEqual(reused.status_code, 401)

    def test_logout_rejects_refresh_token_owned_by_another_user(self):
        other = Staff.objects.create_user(
            username="other-jwt-user",
            password=PASSWORD,
            role="Teacher",
        )
        own_login = self._login()
        other_login = self.client.post(
            "/api/staff/login/",
            {"username": other.username, "password": PASSWORD},
            format="json",
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {own_login.data['access']}"
        )

        response = self.client.post(
            "/api/staff/logout/",
            {"refresh": other_login.data["refresh"]},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.client.credentials()
        still_valid = self.client.post(
            "/api/token/refresh/",
            {"refresh": other_login.data["refresh"]},
            format="json",
        )
        self.assertEqual(still_valid.status_code, 200)

    def test_change_password_invalidates_existing_tokens(self):
        login = self._login()
        old_access = login.data["access"]
        old_refresh = login.data["refresh"]
        new_password = "NewSecurePass!2027"
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {old_access}")

        changed = self.client.post(
            "/api/staff/profile/change-password/",
            {
                "current_password": PASSWORD,
                "new_password": new_password,
                "new_password_confirm": new_password,
            },
            format="json",
        )

        self.assertEqual(changed.status_code, 204)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
        old_access_response = self.client.get("/api/staff/profile/")
        self.assertEqual(old_access_response.status_code, 401)

        self.client.credentials()
        old_refresh_response = self.client.post(
            "/api/token/refresh/", {"refresh": old_refresh}, format="json"
        )
        self.assertEqual(old_refresh_response.status_code, 401)
        old_login = self.client.post(
            "/api/staff/login/",
            {"username": self.user.username, "password": PASSWORD},
            format="json",
        )
        self.assertEqual(old_login.status_code, 401)
        new_login = self.client.post(
            "/api/staff/login/",
            {"username": self.user.username, "password": new_password},
            format="json",
        )
        self.assertEqual(new_login.status_code, 200)

    def test_change_password_validates_current_confirmation_and_strength(self):
        self.client.force_authenticate(self.user)

        wrong_current = self.client.post(
            "/api/staff/profile/change-password/",
            {
                "current_password": "wrong-password",
                "new_password": "AnotherSecurePass!2027",
                "new_password_confirm": "AnotherSecurePass!2027",
            },
            format="json",
        )
        mismatch = self.client.post(
            "/api/staff/profile/change-password/",
            {
                "current_password": PASSWORD,
                "new_password": "AnotherSecurePass!2027",
                "new_password_confirm": "DifferentSecurePass!2027",
            },
            format="json",
        )
        weak = self.client.post(
            "/api/staff/profile/change-password/",
            {
                "current_password": PASSWORD,
                "new_password": "123",
                "new_password_confirm": "123",
            },
            format="json",
        )

        self.assertEqual(wrong_current.status_code, 400)
        self.assertEqual(mismatch.status_code, 400)
        self.assertEqual(weak.status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))


class DocumentationAuthorizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = Staff.objects.create_user(
            username="docs-teacher",
            password=PASSWORD,
            role="Teacher",
        )
        self.admin = Staff.objects.create_user(
            username="docs-admin",
            password=PASSWORD,
            role="Admin",
        )

    def test_documentation_requires_admin_role(self):
        paths = ["/api/schema/", "/api/docs/"]

        for path in paths:
            with self.subTest(path=path, actor="anonymous"):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 401)

        self.client.force_authenticate(self.teacher)
        for path in paths:
            with self.subTest(path=path, actor="teacher"):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 403)

        self.client.force_authenticate(self.admin)
        for path in paths:
            with self.subTest(path=path, actor="admin"):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
