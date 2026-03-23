## Why

Las operaciones CRUD actuales no están preparadas para ejecución offline ni para reconciliar cambios concurrentes entre cliente y servidor. Se requiere un estándar transversal de sincronización Offline-First para evitar pérdida de datos, detectar conflictos de versión y habilitar reintentos seguros.

## What Changes

- Añadir campos de sincronización (`syncStatus`, `version`, `localUpdatedAt`) en tablas operativas: `students`, `staff`, `attendances`, `assignment`, `student_grades`, `enrollments`.
- Asegurar UUID como primary key en las tablas operativas objetivo para prevenir colisiones en creación offline.
- Definir reglas de creación offline: ID UUID del cliente, `syncStatus='pending'`, `version=1`, `localUpdatedAt` actual.
- Definir reglas de edición local: cada update marca `syncStatus='pending'` y actualiza `localUpdatedAt`.
- Implementar validación de concurrencia optimista en backend comparando `request.version` contra `db.version`.
- En conflicto de versión, responder `409 Conflict` y propagar estado de conflicto para que el cliente marque `syncStatus='conflict'`.
- Garantizar exposición de los campos de sincronización en serializers para intercambio API.

## Capabilities

### New Capabilities
- `offline-first-sync-versioning`: Infraestructura de persistencia y API para sincronización Offline-First con versionado optimista y manejo de conflictos.

### Modified Capabilities
- (none)

## Impact

- Modelos y migraciones Django en módulos `students`, `staff`, `attendance`, `grades`, `academics`.
- Repositorios/casos de uso de persistencia para creación/actualización con reglas offline-first y control de versión.
- Capa HTTP (views/serializers) para recibir/enviar `syncStatus`, `version`, `localUpdatedAt` y responder `409` en conflictos.
- Sin cambios en tablas del sistema Django (`auth`, `sessions`, `content_types`, `migrations`).
