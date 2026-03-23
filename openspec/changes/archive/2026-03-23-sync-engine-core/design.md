## Context

El backend está compuesto por módulos de dominio (`students`, `staff`, `attendance`, `grades`, `academics`) con repositorios separados y sin una convención uniforme de sincronización offline. Hoy no existe control de versiones optimista transversal ni señalización de estado de sincronización, lo que provoca riesgo de sobrescrituras silenciosas y reconciliación manual de conflictos.

Este cambio es transversal y afecta modelos, migraciones, persistencia y contratos de API para múltiples tablas operativas, con especial cuidado en no tocar tablas del sistema Django.

## Goals / Non-Goals

**Goals:**
- Estandarizar campos de sincronización (`syncStatus`, `version`, `localUpdatedAt`) en tablas operativas objetivo.
- Forzar UUID como primary key en tablas operativas objetivo para creación offline segura.
- Implementar control de concurrencia optimista en updates con comparación de versión y respuesta `409 Conflict`.
- Ajustar lógica de creación/edición para soportar ciclo offline-first (`pending` -> `synced` o `conflict`).
- Exponer campos de sincronización en serializers para comunicación API.

**Non-Goals:**
- Cambiar tablas del sistema Django (`auth`, `sessions`, `content_types`, `migrations`).
- Implementar motor de sincronización distribuido o cola de eventos en esta fase.
- Resolver automáticamente conflictos complejos del lado servidor (solo detección y rechazo con `409`).

## Decisions

1. **Campos de sincronización normalizados por tabla operativa**
   - Se agregan en cada tabla objetivo: `syncStatus` (`varchar(20)` con valores `synced|pending|conflict`), `version` (`int4 NOT NULL default 1`) y `localUpdatedAt` (`timestamptz default now()`).
   - **Rationale:** contrato uniforme entre backend y clientes TypeScript.
   - **Alternativas:** tabla de metadatos de sync separada por entidad (descartada por joins extra y mayor complejidad operativa inicial).

2. **Persistencia explícita de estado offline-first en create/update**
   - Create offline: el backend acepta/preserva UUID del cliente; si crea server-side, mantiene UUID. Para registros nuevos sincronizables, estado inicial `pending`, `version=1`, `localUpdatedAt=now()`.
   - Update: siempre actualiza `localUpdatedAt`; en flujo local marca `pending`; en update validado por servidor marca `synced` si éxito.
   - **Rationale:** alinea ciclo de vida de sync con semántica del cliente.
   - **Alternativas:** triggers DB para estado/version (descartado por acoplamiento y baja trazabilidad en capa dominio).

3. **Concurrencia optimista en repositorios de actualización**
   - Los comandos de update incluyen `version` solicitada.
   - Regla: `request.version == db.version` => aplicar cambios y `db.version += 1`; respuesta con `syncStatus='synced'`.
   - Si no coincide => lanzar excepción de conflicto de versión y mapear a HTTP 409.
   - **Rationale:** evita lost updates con costo bajo.
   - **Alternativas:** locking pesimista (descartado por impacto de rendimiento y experiencia offline).

4. **Migración de PK a UUID donde no exista**
   - Para tablas operativas que aún no tengan UUID PK (por ejemplo `attendances`, `student_grades`, y cualquier `assignment` existente), se migra PK a UUID sin tocar tablas de sistema.
   - **Rationale:** evitar colisiones entre dispositivos y soportar creación offline.
   - **Alternativas:** IDs temporales cliente + remapeo posterior (descartado por complejidad de reconciliación).

## Risks / Trade-offs

- [Riesgo] Migraciones de PK pueden afectar FKs existentes y datos en producción → Mitigación: migraciones en pasos, backfill de UUID y validación de integridad referencial antes de constraints finales.
- [Riesgo] Clientes antiguos sin `version` en update → Mitigación: validar payload y devolver error explícito de contrato hasta actualización del cliente.
- [Trade-off] Más campos y lógica en serializers/use-cases → Mitigación: centralizar utilidades de sync y pruebas de contrato por módulo.
- [Riesgo] Divergencia semántica entre “edición local” y “update confirmado por backend” → Mitigación: documentar claramente transición de estados y pruebas de flujo.

## Migration Plan

1. Auditar tablas objetivo existentes y detectar ausencia de tabla `assignment` para decidir creación o adaptación.
2. Crear migraciones por app para agregar campos de sync y defaults SQL equivalentes.
3. Migrar PK a UUID en tablas operativas que aún no lo tengan, preservando FKs.
4. Actualizar DTOs/comandos/repositorios para incluir `version` y reglas de estado.
5. Actualizar views para mapear conflicto de versión a `409 Conflict`.
6. Exponer campos de sync en serializers de lectura/escritura.
7. Ejecutar pruebas de regresión CRUD y concurrencia optimista.

Rollback:
- Revertir migraciones de campos/PK en orden inverso.
- Mantener bandera de despliegue para desactivar validación estricta de versión si surge incompatibilidad de cliente.

## Open Questions

- La tabla `assignment` no aparece en el estado actual del repositorio: ¿debe crearse en este cambio o se refiere a una tabla existente con otro nombre?
- ¿El backend debe aceptar updates sin `version` durante una ventana de compatibilidad o debe ser obligatorio inmediatamente?
- ¿`syncStatus='conflict'` debe persistirse en servidor además de marcarse localmente cuando ocurre `409`?
