## Context

El backend actual usa Django por apps funcionales (`students`, `staff`, `attendance`, `grades`, `academics`) y concentra reglas de negocio en views/serializers/model helpers. Esta estructura acelera entregas iniciales pero introduce acoplamiento entre framework, persistencia y lógica de dominio, dificultando pruebas unitarias de reglas críticas y cambios transversales.

La propuesta define una transición incremental a Clean Architecture sin cambiar contratos HTTP existentes. El cambio debe convivir con código legado durante varias iteraciones, priorizando continuidad operativa y reducción de riesgo.

## Goals / Non-Goals

**Goals:**
- Establecer límites explícitos entre capas `domain`, `application`, `infrastructure` e `interfaces`.
- Mover reglas de negocio y casos de uso fuera de views/serializers.
- Introducir puertos (interfaces) para repositorios/servicios usados por casos de uso.
- Mantener compatibilidad de endpoints y payloads durante la migración.
- Habilitar pruebas unitarias de dominio y aplicación sin dependencia directa de Django ORM.

**Non-Goals:**
- Reescribir todo el sistema en una sola iteración.
- Rediseñar contratos de API públicos en esta fase.
- Cambiar proveedor de base de datos o stack de ejecución.
- Aplicar optimizaciones de performance no relacionadas al desacoplamiento arquitectónico.

## Decisions

1. **Arquitectura objetivo por feature, no por big-bang**
   - Decisión: migrar por casos de uso de alto valor, manteniendo coexistencia temporal con estructura por apps.
   - Racional: minimiza riesgo de regresiones y permite validación progresiva.
   - Alternativa considerada: reestructuración completa inmediata; descartada por alto costo y riesgo operacional.

2. **Dependencias dirigidas hacia adentro**
   - Decisión: `interfaces` y `infrastructure` dependen de `application`; `application` depende de `domain`; `domain` no depende de frameworks.
   - Racional: preserva independencia del dominio y facilita pruebas.
   - Alternativa considerada: mantener llamadas directas ORM en views; descartada por perpetuar acoplamiento.

3. **Casos de uso como unidad de orquestación**
   - Decisión: cada flujo de negocio relevante se representa como caso de uso en capa de aplicación.
   - Racional: mejora trazabilidad funcional y testabilidad.
   - Alternativa considerada: servicios utilitarios genéricos; descartada por falta de frontera clara de responsabilidades.

4. **Adaptadores Django para repositorios/serialización**
   - Decisión: implementar adaptadores en infraestructura que cumplan puertos definidos por aplicación.
   - Racional: permite aislar ORM y detalles de persistencia del dominio.
   - Alternativa considerada: acceso ORM desde dominio; descartada por violar Clean Architecture.

5. **Estrategia de compatibilidad de API**
   - Decisión: conservar rutas, métodos y esquemas de respuesta existentes, sustituyendo sólo la orquestación interna.
   - Racional: evita breaking changes en clientes consumidores.
   - Alternativa considerada: versionado inmediato de APIs; pospuesto para una iniciativa específica.

## Risks / Trade-offs

- **[Riesgo] Duplicación temporal de lógica entre capa nueva y legado** → **Mitigación:** migrar flujo por flujo con eliminación explícita de código viejo al cerrar cada tarea.
- **[Riesgo] Inconsistencia de patrones entre módulos** → **Mitigación:** definir convenciones mínimas de carpetas, naming y límites de dependencia desde el inicio.
- **[Riesgo] Mayor complejidad inicial para el equipo** → **Mitigación:** incluir ejemplos base por módulo y checklist de revisión arquitectónica en PRs.
- **[Riesgo] Regresiones funcionales durante la transición** → **Mitigación:** añadir pruebas unitarias de casos de uso y smoke tests de endpoints críticos antes de migrar cada flujo.

## Migration Plan

1. Definir estructura base de capas y paquetes compartidos para un módulo piloto.
2. Seleccionar 1-2 casos de uso críticos y migrarlos completamente con adaptadores.
3. Mantener views/serializers como fachada y delegar en casos de uso nuevos.
4. Repetir por módulo (students, staff, attendance, grades, academics) con validación incremental.
5. Eliminar lógica legado equivalente tras verificación funcional.
6. Consolidar reglas de arquitectura y documentación interna para nuevas funcionalidades.

**Rollback:** si un flujo migrado falla en producción, restaurar temporalmente la ruta de ejecución anterior en views/serializers (manteniendo endpoint), y reactivar migración tras corregir caso de uso/adaptador afectado.

## Open Questions

- ¿Qué módulo se toma oficialmente como piloto (recomendado: `students` por cobertura funcional)?
- ¿Se adoptará una librería de inyección de dependencias o se mantendrá wiring manual en esta fase?
- ¿Qué nivel mínimo de cobertura de pruebas unitarias por caso de uso será criterio de “done”?
