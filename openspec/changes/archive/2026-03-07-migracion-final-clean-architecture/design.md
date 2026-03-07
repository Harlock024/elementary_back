## Context

El backend de Elementary tiene una arquitectura parcialmente migrada a Clean Architecture. La migración piloto en `students` estableció las bases, y se extendió a otros módulos con estructura de carpetas pero implementación incompleta.

**Estado actual:**
- Módulos con estructura Clean Architecture: `students`, `academics`, `grades`, `attendance`, `staff`
- Endpoints migrados: operaciones GET (listado/detalle) y POST (creación)
- Endpoints legado: PUT, PATCH, DELETE que acceden directamente a modelos Django/ORM desde `views.py`
- Documentación base: `docs/clean-architecture/` con guía de implementación y checklist
- Spec existente: `openspec/specs/clean-architecture-boundaries/` define reglas de dependencia

**Módulos por completar:**
| Módulo | Endpoints legado pendientes |
|--------|----------------------------|
| students | PUT, DELETE, PATCH |
| academics | PUT, PATCH (SchoolGrade, Group, Subject, ClassRoom, Enrollment) |
| grades | PUT, DELETE |
| attendance | PATCH |
| staff | PUT, DELETE |

## Goals / Non-Goals

**Goals:**
- Completar migración de todos los endpoints a use cases en capa `application`
- Mantener compatibilidad total de API (rutas, métodos, contratos)
- Eliminar acceso directo a ORM desde vistas
- Alcanzar completion gate definido en documentación existente
- Asegurar cobertura de testing para use cases migrados

**Non-Goals:**
- Refactorizar modelos Django existentes
- Cambiar estructura de URLs o contratos de API
- Migrar a otro framework o base de datos
- Implementar nuevas funcionalidades de negocio
- Cambiar autenticación/autorización existente

## Decisions

### 1. Patrón para use cases de escritura
**Decisión**: Seguir el patrón establecido en `create_student.py` con Commands para entrada.
**Alternativas**: DTOs request/response separados, parámetros directos.
**Razón**: Consistencia con código existente, validación explícita en Commands.

### 2. Orden de migración por módulo
**Decisión**: Completar un módulo antes de pasar al siguiente (students → staff → academics → grades → attendance).
**Alternativas**: Migrar por tipo de operación (todos los PUT, luego todos los DELETE).
**Razón**: Permite validar completion gate por módulo y facilita rollback parcial.

### 3. Naming de use cases de escritura
**Decisión**: `update_<resource>.py` y `delete_<resource>.py` en `application/use_cases/`.
**Alternativas**: Agrupar en un solo archivo CRUD, usar classes en lugar de funciones.
**Razón**: Consistencia con naming existente (`create_student.py`, `get_students.py`).

### 4. Manejo de soft delete vs hard delete
**Decisión**: Mantener comportamiento actual de cada endpoint (mayoría hard delete).
**Alternativas**: Migrar todos a soft delete.
**Razón**: Preservar contrato existente, cambio de política es un cambio de negocio fuera de scope.

### 5. DTOs de actualización
**Decisión**: Crear `UpdateXCommand` con campos opcionales para soportar PATCH parcial.
**Alternativas**: Commands separados para PUT (completo) y PATCH (parcial).
**Razón**: Un solo Command simplifica, la lógica de merge va en el use case.

## Risks / Trade-offs

**[Regresión en APIs existentes]** → Smoke tests obligatorios por endpoint migrado antes de merge.

**[Inconsistencia temporal durante migración]** → Aceptar inconsistencia por sprint si se completan módulos enteros.

**[Complejidad adicional para operaciones simples]** → Trade-off aceptado por consistencia arquitectónica y testabilidad.

**[Posibles errores de mapeo DTO ↔ Entity]** → Tests unitarios de use cases con casos edge (campos null, parciales).

## Migration Plan

1. **Por cada módulo** (en orden: students, staff, academics, grades, attendance):
   - Crear DTOs de comando (`UpdateXCommand`)
   - Crear use cases (`update_x.py`, `delete_x.py`)
   - Extender repositorios con métodos `update()` y `delete()`
   - Refactorizar views para delegar a use cases
   - Eliminar imports directos de modelos en views
   - Agregar tests unitarios y smoke tests
   - Verificar completion gate

2. **Rollback**: Revertir commit de view individual si falla smoke test.

## Open Questions

- ¿Incluir validación de permisos en use cases o mantenerla en views? (Decisión pendiente: revisar con equipo)
