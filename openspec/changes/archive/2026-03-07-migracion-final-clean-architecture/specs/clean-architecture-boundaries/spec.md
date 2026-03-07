## MODIFIED Requirements

### Requirement: Application use-case orchestration
The system SHALL implement business workflows as explicit application use cases that orchestrate domain rules through input/output boundaries.

#### Scenario: API operation delegates to use case
- **WHEN** an API endpoint for a migrated workflow is invoked
- **THEN** the interface layer delegates orchestration to exactly one application use-case entry point

#### Scenario: All CRUD operations use use cases
- **WHEN** any CRUD operation (GET, POST, PUT, PATCH, DELETE) is performed on a migrated endpoint
- **THEN** the operation is handled by a corresponding use case in the application layer

#### Scenario: Write operations use Command DTOs
- **WHEN** a write operation (POST, PUT, PATCH) is delegated to a use case
- **THEN** the use case accepts a typed Command DTO as input parameter

### Requirement: Incremental migration governance
The system SHALL migrate modules incrementally with explicit completion criteria for each migrated workflow.

#### Scenario: Workflow migration completion gate
- **WHEN** a workflow migration task is marked as completed
- **THEN** the workflow has delegated execution to use case layer, has tests for core rules, and legacy duplicated logic has been removed

#### Scenario: Full module migration completion
- **WHEN** all CRUD operations in a module are migrated
- **THEN** the module views file contains no direct ORM access for any endpoint operation
