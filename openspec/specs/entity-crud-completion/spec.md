# entity-crud-completion Specification

## Purpose
TBD - created by archiving change migracion-final-clean-architecture. Update Purpose after archive.
## Requirements
### Requirement: Update use case orchestration
The system SHALL implement update operations (PUT/PATCH) through explicit application use cases that accept typed command DTOs.

#### Scenario: PUT endpoint delegates to update use case
- **WHEN** a PUT request is made to a migrated endpoint
- **THEN** the interface layer creates an UpdateCommand DTO and delegates to the corresponding update use case

#### Scenario: PATCH endpoint handles partial updates
- **WHEN** a PATCH request is made with partial data
- **THEN** the update use case merges only provided fields with existing entity data

### Requirement: Delete use case orchestration
The system SHALL implement delete operations through explicit application use cases.

#### Scenario: DELETE endpoint delegates to delete use case
- **WHEN** a DELETE request is made to a migrated endpoint
- **THEN** the interface layer delegates to the corresponding delete use case with the resource identifier

#### Scenario: Delete use case returns appropriate response
- **WHEN** a delete use case successfully removes a resource
- **THEN** the use case completes without exception and the interface returns 204 status

### Requirement: Repository write operations
The system SHALL extend repository ports with update and delete methods for each entity requiring write operations.

#### Scenario: Repository update method signature
- **WHEN** an update use case needs to persist changes
- **THEN** the repository port defines an update method accepting the entity identifier and update data

#### Scenario: Repository delete method signature
- **WHEN** a delete use case needs to remove a resource
- **THEN** the repository port defines a delete method accepting the entity identifier

### Requirement: Command DTOs for write operations
The system SHALL define typed Command DTOs for all update operations with optional fields for PATCH support.

#### Scenario: UpdateCommand with optional fields
- **WHEN** an UpdateCommand DTO is defined for an entity
- **THEN** all updateable fields are declared as Optional types to support partial updates

#### Scenario: Command validation at boundary
- **WHEN** an UpdateCommand is instantiated with invalid data
- **THEN** the DTO raises a validation error before reaching the use case logic

