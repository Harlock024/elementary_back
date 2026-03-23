## 1. Auditoría y alcance de entidades operativas

- [x] 1.1 Confirmar entidades/tablas objetivo (`students`, `staff`, `attendances`, `assignment`, `student_grades`, `enrollments`) y mapear el modelo real para `assignment` en el repositorio
- [x] 1.2 Verificar estado actual de primary keys en entidades objetivo e identificar tablas que requieren migración a UUID

## 2. Cambios de esquema y migraciones

- [x] 2.1 Agregar en modelos objetivo los campos `syncStatus` (`max_length=20`), `version` (`IntegerField default=1`) y `localUpdatedAt` (`DateTimeField default=now`)
- [x] 2.2 Crear migraciones por app para añadir columnas con defaults compatibles en Postgres sin tocar tablas del sistema Django
- [x] 2.3 Migrar a UUID primary key en tablas operativas que no lo tengan (`attendances`, `student_grades`, y `assignment` si aplica), preservando integridad referencial

## 3. Contratos de aplicación para concurrencia optimista

- [x] 3.1 Extender DTOs/comandos de update para requerir `version` de la solicitud en entidades objetivo
- [x] 3.2 Implementar excepción de conflicto de versión por dominio para representar mismatch de concurrencia

## 4. Lógica de persistencia offline-first

- [x] 4.1 Actualizar repositorios de create para preservar UUID cliente y establecer estado inicial `pending`, `version=1`, `localUpdatedAt` actual
- [x] 4.2 Actualizar repositorios de update para validar `request.version == db.version` antes de persistir cambios
- [x] 4.3 En update exitoso, incrementar versión y devolver `syncStatus='synced'`; en mismatch, lanzar conflicto para respuesta HTTP 409 y contexto de `conflict`

## 5. API y serialización

- [x] 5.1 Exponer `syncStatus`, `version` y `localUpdatedAt` en serializers de entidades objetivo
- [x] 5.2 Mapear excepciones de conflicto de versión a HTTP 409 en views/endpoints de update afectados

## 6. Validación y cobertura

- [x] 6.1 Agregar/actualizar pruebas unitarias de repositorio para create offline, update exitoso y conflicto por versión
- [x] 6.2 Ejecutar migraciones y suite relevante para verificar integridad de esquema, serialización y códigos de respuesta
