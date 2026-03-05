## 1. Arquitectura base y convenciones

- [x] 1.1 Definir estructura de carpetas por capas (`domain`, `application`, `infrastructure`, `interfaces`) para un módulo piloto
- [x] 1.2 Documentar reglas de dependencia entre capas y convenciones de naming/imports
- [x] 1.3 Crear checklist de revisión arquitectónica para PRs de migración

## 2. Piloto de migración incremental

- [x] 2.1 Seleccionar módulo piloto y mapear 1-2 workflows críticos a casos de uso
- [x] 2.2 Implementar casos de uso de aplicación para workflows piloto con contratos de entrada/salida
- [x] 2.3 Definir puertos de repositorio/servicios requeridos por los casos de uso piloto
- [x] 2.4 Implementar adaptadores de infraestructura (ORM/servicios externos) que cumplan los puertos
- [x] 2.5 Adaptar views/serializers del piloto para delegar orquestación a casos de uso

## 3. Compatibilidad y calidad

- [x] 3.1 Verificar que rutas, métodos y payloads públicos del piloto se mantienen compatibles
- [x] 3.2 Añadir pruebas unitarias para reglas de dominio y casos de uso migrados
- [x] 3.3 Ejecutar smoke tests de endpoints críticos del módulo piloto
- [x] 3.4 Eliminar lógica duplicada legado cubierta por los casos de uso migrados

## 4. Escalado a módulos restantes

- [x] 4.1 Repetir patrón de migración en `students`, `staff`, `attendance`, `grades` y `academics` por workflow
- [x] 4.2 Aplicar criterios de completion gate (delegación a use case + pruebas + remoción de legado) por cada workflow
- [x] 4.3 Consolidar documentación final de arquitectura y guía de incorporación para nuevas features
