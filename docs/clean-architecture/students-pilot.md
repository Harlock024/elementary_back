## Módulo piloto seleccionado

- Módulo: `students`
- Motivo: alto impacto funcional y bajo riesgo de cambios de contrato HTTP en primera iteración.

## Workflows piloto mapeados

1. `GET /api/students/` y `GET /api/students/<id>/`
   - Caso de uso: consulta de estudiantes (listado/detalle).
2. `POST /api/students/`
   - Caso de uso: creación de estudiante con matrícula (enrollment) activa.

## Estructura por capas (piloto)

```
students/
├── domain/
│   ├── entities/
│   ├── exceptions/
│   └── repositories/
├── application/
│   ├── dto/
│   └── use_cases/
├── infrastructure/
│   └── repositories/
└── interfaces/
    └── http/
```

## Reglas de dependencia

- `domain` no importa módulos Django, DRF ni adaptadores.
- `application` depende de contratos en `domain`, nunca de ORM/serializers.
- `infrastructure` implementa puertos definidos por `application/domain`.
- `interfaces` (views) solo orquesta request/response y delega en casos de uso.

## Convenciones de naming/imports

- Casos de uso: `<action>_<resource>.py` en `application/use_cases/`.
- Puertos: `*Repository` en `domain/repositories/`.
- Adaptadores Django: `django_<resource>_repository.py` en `infrastructure/repositories/`.
- DTOs de entrada: `*Command` en `application/dto/`.
