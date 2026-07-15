# AGENTS.md

## Project Overview

Django 5.2 REST API for an elementary school management system. PostgreSQL backend, JWT auth, Swagger docs.

## Quick Commands

```bash
# Activate venv first
source venv/bin/activate

# Run dev server
python manage.py runserver

# Run all tests
python manage.py test

# Run single app tests
python manage.py test staff
python manage.py test students
python manage.py test academics

# Run single test class
python manage.py test staff.tests.StaffUseCaseTests

# Run single test method
python manage.py test staff.tests.StaffUseCaseTests.test_create_staff_validates_required_fields

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Architecture

Clean Architecture (domain → application → infrastructure → interfaces/http). Each app follows this structure:

```
app/
  domain/
    entities/        # Domain entities (dataclasses or raw dicts)
    repositories/    # Repository Protocol interfaces
    exceptions/      # Domain-specific exceptions
  application/
    dto/             # Command/data transfer objects
    use_cases/       # Business logic classes with .execute() method
  infrastructure/
    repositories/    # Django ORM implementations of repository protocols
  interfaces/
    http/            # Factory functions that wire repositories into use cases
  models.py          # Django models
  serializer.py      # DRF serializers
  views.py           # API views (use factory functions from interfaces/http/)
  urls.py
```

Views call `build_*_use_case()` factory functions (in `interfaces/http/`) which instantiate the correct repository and use case. Do not call repositories directly from views.

## Apps & API Prefixes

| App | Prefix | Domain |
|-----|--------|--------|
| `staff` | `/api/staff/` | User management (custom auth model) |
| `students` | `/api/students/` | Student records |
| `academics` | `/api/academics/` | School grades, groups, subjects, enrollments, classrooms, promotions |
| `attendance` | `/api/attendances/` | Attendance tracking |
| `grades` | `/api/grades/` | Student grades and grading criteria |
| `assignments` | `/api/assignments/` | Assignments |

Swagger UI: `/api/docs/` | Schema: `/api/schema/`

## Auth & Roles

- Custom user model: `staff.Staff` (extends `AbstractUser`, UUID primary key)
- `AUTH_USER_MODEL = 'staff.Staff'` in settings
- JWT auth via `djangorestframework_simplejwt` — login at `/api/staff/login/`
- Roles defined in middleware: Admin, Superuser, Principal, Teacher
- `Staff.ROLE_CHOICES` only lists Admin/Teacher — Superuser/Principal are handled in middleware only
- `RoleScopeMiddleware` sets `request.scope` based on role: Admin/Superuser/Principal → `'all'`, Teacher → `'Teacher'`
- `IsAdmin` permission class (in `middleware.py`) allows Admin, Superuser, Principal
- Most endpoints require `IsAdmin`; `SubjectViewSet` and `ClassRoomViewSet.get` have custom role checks

## Key Gotchas

- **CORS**: Only allows `http://localhost:4321` — frontend runs on that port
- **DB**: PostgreSQL on localhost:5432, database `elementary_db`, user `harlock024`
- **No lint/typecheck configured**: `pyrightconfig.json` has `typeCheckingMode: "off"`. No flake8/ruff/black. Don't run lint commands — there are none
- **UUID PKs**: All models except `StudentGrade` (uses default int) and `GradingCriteria` (UUID) use UUID primary keys
- **Enrollment states**: Spanish strings — `'activo'` for active enrollments
- **`Student.generate_enrollment_number()`**: Auto-generates `E{year}{sequence}` format numbers
- **Duplicate middleware**: `CommonMiddleware` appears twice in MIDDLEWARE list (line 76 and 82)
- **`staff.views`** has legacy function-based views (`create_professor`, `list_professors`) alongside clean-architecture class views — prefer the class views pattern

## Testing

- Tests use `django.test.TestCase` + `rest_framework.test.APIClient`
- Unit tests inject `_InMemory*Repository` fakes (defined in test files)
- Endpoint tests use `APIClient` and hit real DB (SQLite in-memory for tests)
- No pytest, no fixtures files, no factory_boy — just inline setup
- No test runner config beyond Django defaults
