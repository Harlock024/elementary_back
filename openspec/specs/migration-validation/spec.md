# migration-validation Specification

## Purpose
TBD - created by archiving change migracion-final-clean-architecture. Update Purpose after archive.
## Requirements
### Requirement: Legacy code removal verification
The system SHALL verify that migrated views do not contain direct ORM model access for migrated operations.

#### Scenario: No direct model imports for migrated operations
- **WHEN** a view file for a fully migrated module is analyzed
- **THEN** no direct imports of Django models are used for CRUD operations (only for permission classes or unrelated concerns)

#### Scenario: No ORM queries in views
- **WHEN** a migrated endpoint handler is analyzed
- **THEN** no `Model.objects.get()`, `Model.objects.filter()`, or similar ORM calls are present

### Requirement: Completion gate validation
The system SHALL provide verification that each migrated workflow meets completion criteria.

#### Scenario: Workflow completion checklist
- **WHEN** a workflow migration is marked complete
- **THEN** the workflow has: (1) delegated to use case, (2) tests for use case, (3) no duplicated legacy logic

#### Scenario: Module completion status
- **WHEN** all endpoints in a module pass completion gate
- **THEN** the module is marked as fully migrated in documentation

### Requirement: Test coverage for migrated use cases
The system SHALL have unit tests for each migrated use case covering success and error paths.

#### Scenario: Use case unit test exists
- **WHEN** a new use case is created for a migrated operation
- **THEN** a corresponding unit test file exists in the appropriate test location

#### Scenario: Smoke test for migrated endpoint
- **WHEN** a view endpoint is migrated to use a use case
- **THEN** a smoke test verifies the endpoint responds correctly with expected status codes

