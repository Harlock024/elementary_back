## Why

El proyecto tiene una migración parcial a Clean Architecture iniciada como piloto en `students` y extendida a otros módulos (`academics`, `grades`, `attendance`, `staff`). Sin embargo, múltiples endpoints aún mantienen lógica legado con acceso directo a modelos ORM en las vistas, violando las reglas de dependencia establecidas. Completar esta migración es necesario para lograr consistencia arquitectónica, facilitar el testing unitario y cumplir los criterios de completion gate definidos en la documentación.

## What Changes

- Migrar todos los endpoints legado (PUT, DELETE, PATCH) en cada módulo a use cases de `application`.
- Crear puertos y adaptadores faltantes para operaciones de actualización y eliminación.
- Eliminar acceso directo a modelos Django/ORM desde la capa `interfaces/http`.
- Remover lógica de negocio duplicada en `views.py` una vez migrada.
- Añadir pruebas unitarias de use cases y smoke tests para endpoints migrados.

## Capabilities

### New Capabilities
- `entity-crud-completion`: Casos de uso completos para operaciones CRUD (update, delete) en todos los módulos.
- `migration-validation`: Validación automatizada de reglas de dependencia entre capas.

### Modified Capabilities
- `clean-architecture-boundaries`: Se extienden los requisitos para cubrir operaciones de escritura (PUT/PATCH/DELETE), no solo lectura y creación.

## Impact

- **Código afectado**: `views.py` de todos los módulos (`students`, `academics`, `grades`, `attendance`, `staff`).
- **Nuevos archivos**: Use cases para update/delete en `application/use_cases/`, DTOs de comando en `application/dto/`, adaptadores en `infrastructure/repositories/`.
- **APIs**: Sin cambios de contrato externo (mismas rutas, métodos y respuestas).
- **Testing**: Requerirá nuevas pruebas unitarias por cada use case y smoke tests de integración.
- **Dependencias**: Sin nuevas dependencias externas.
