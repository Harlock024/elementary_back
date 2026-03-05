## Guía de implementación Clean Architecture

Esta guía define cómo crear o migrar workflows en el backend manteniendo compatibilidad de API.

## Flujo recomendado por feature

1. Definir caso de uso en `application/use_cases`.
2. Declarar puertos necesarios en `domain/repositories`.
3. Implementar adaptadores en `infrastructure`.
4. Delegar desde capa HTTP (`views`) al caso de uso.
5. Añadir pruebas unitarias de caso de uso y smoke tests de endpoint.
6. Eliminar lógica duplicada legado del workflow migrado.

## Completion gate por workflow

Un workflow migrado se considera completo cuando:

- Delega la orquestación a un caso de uso de `application`.
- Usa puertos/adaptadores para acceso a persistencia/servicios.
- Mantiene ruta, método y contrato de respuesta del endpoint existente.
- Tiene pruebas unitarias y smoke tests verdes.
- No mantiene lógica de negocio duplicada en la vista.

## Plantilla mínima para nuevas features

```
<app>/
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

## Referencias del piloto

- Estructura y reglas base: `docs/clean-architecture/students-pilot.md`
- Checklist de revisión: `docs/clean-architecture/review-checklist.md`
