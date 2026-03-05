## Why

La base de código actual está organizada por apps Django, pero mezcla reglas de dominio, casos de uso y acceso a datos en capas de framework, lo que dificulta pruebas aisladas y evolución segura. Es necesario iniciar una refactorización estructurada a Clean Architecture para reducir acoplamiento y mejorar mantenibilidad a mediano plazo.

## What Changes

- Introducir una arquitectura por capas explícitas (`domain`, `application`, `infrastructure`, `interfaces`) con límites claros de dependencias.
- Definir contratos (puertos) para persistencia y servicios externos usados por casos de uso.
- Migrar gradualmente flujos críticos de los módulos académicos (estudiantes, staff, asistencia, calificaciones y académicos) hacia casos de uso en capa de aplicación.
- Adaptar views/serializers para actuar como capa de interfaz, delegando lógica a casos de uso.
- Agregar lineamientos de estructura de paquetes y convenciones para nuevas funcionalidades.

elementary_back/
├── elementary_back/          # Configuración Django
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/                     # Núcleo de la aplicación
│   ├── staff/
│   │   ├── domain/           # Entidades y interfaces
│   │   │   ├── entities/
│   │   │   │   └── staff_entity.py
│   │   │   ├── repositories/
│   │   │   │   └── staff_repository.py
│   │   │   └── exceptions/
│   │   │       └── staff_exceptions.py
│   │   │
│   │   ├── application/      # Casos de Uso
│   │   │   ├── dto/
│   │   │   │   └── staff_dto.py
│   │   │   └── use_cases/
│   │   │       ├── create_staff.py
│   │   │       ├── get_staff.py
│   │   │       └── login_staff.py
│   │   │
│   │   └── infrastructure/   # Adaptadores Django
│   │       ├── models/
│   │       │   └── staff_model.py
│   │       ├── repositories/
│   │       │   └── django_staff_repository.py
│   │       ├── serializers/
│   │       │   └── staff_serializer.py
│   │       ├── views/
│   │       │   └── staff_views.py
│   │       └── urls.py
│   │
│   ├── students/
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   │
│   ├── academics/
│   ├── attendance/
│   └── grades/
│
├── shared/                   # Código compartido
│   ├── domain/
│   │   ├── entity.py         # Base entity
│   │   ├── repository.py     # Base repository
│   │   └── exceptions.py     # Excepciones comunes
│   │
│   └── infrastructure/
│       ├── di/               # Inyección de dependencias
│       │   └── container.py
│       └── pagination/
│           └── paginator.py
│
└── tests/                    # Tests
    ├── unit/
    └── integration/


## Capabilities

### New Capabilities
- `clean-architecture-boundaries`: Define and enforce clean architecture boundaries for core academic backend workflows.

### Modified Capabilities
- Ninguna.

## Impact

- Código afectado: módulos Django `students`, `staff`, `attendance`, `grades`, `academics`, y configuración del proyecto.
- APIs: se mantienen endpoints públicos existentes; cambios internos de orquestación y responsabilidades.
- Dependencias: no se requiere framework adicional obligatorio para iniciar; puede añadirse tooling de arquitectura/lint en fases posteriores.
- Operación: migración incremental para minimizar riesgo y evitar cambios disruptivos en producción.
