## ADDED Requirements

### Requirement: Operational entities SHALL include synchronization metadata
The system SHALL add synchronization metadata to all operational entities in scope (`students`, `staff`, `attendances`, `assignment`, `student_grades`, `enrollments`): `syncStatus`, `version`, and `localUpdatedAt`.

#### Scenario: Create schema with sync metadata
- **WHEN** database migrations are applied for operational entities in scope
- **THEN** each target table MUST contain `syncStatus` (`VARCHAR(20)` constrained to `synced|pending|conflict`), `version` (`INTEGER NOT NULL DEFAULT 1`), and `localUpdatedAt` (`TIMESTAMPTZ DEFAULT now()`) columns

### Requirement: Operational entities SHALL use UUID primary keys
The system MUST preserve or migrate operational entities in scope to UUID primary keys to prevent ID collisions during offline creation.

#### Scenario: Validate primary key type after migration
- **WHEN** schema validation runs after migration
- **THEN** every target operational table MUST expose a UUID primary key and no integer primary key for those entities

### Requirement: Offline creation SHALL initialize pending synchronization state
The system SHALL support offline-first creation semantics by preserving client-generated UUID and initializing synchronization fields consistently.

#### Scenario: Create new operational record from offline client
- **WHEN** a client submits a new record with client-generated UUID while offline synchronization is pending
- **THEN** the persisted record MUST keep the UUID, set `syncStatus` to `pending`, set `version` to `1`, and set `localUpdatedAt` to current timestamp

### Requirement: Local edits SHALL mark records as pending and refresh local timestamp
The system MUST update synchronization metadata for any client-originated local edit before server reconciliation.

#### Scenario: Apply local edit to existing record
- **WHEN** a client edits a synchronized record locally
- **THEN** the record metadata MUST set `syncStatus` to `pending` and refresh `localUpdatedAt` to the edit timestamp

### Requirement: Backend updates SHALL enforce optimistic version checks
The system MUST validate optimistic concurrency during update operations by comparing request version with stored version.

#### Scenario: Update accepted on matching version
- **WHEN** an update request arrives with `request.version` equal to `db.version`
- **THEN** the system MUST apply the update, increment stored `version` by one, and return `syncStatus` as `synced`

#### Scenario: Update rejected on version mismatch
- **WHEN** an update request arrives with `request.version` different from `db.version`
- **THEN** the system MUST reject the update with HTTP `409 Conflict` and return conflict information for the client to mark local state as `syncStatus='conflict'`

### Requirement: Synchronization fields SHALL be exposed in API serializers
The system SHALL include `syncStatus`, `version`, and `localUpdatedAt` in serializer contracts for operational entities in scope.

#### Scenario: Read and write synchronization fields through API
- **WHEN** an API consumer requests or updates an operational entity in scope
- **THEN** serializer payloads MUST include synchronization fields in responses and support required write-path fields for concurrency validation
