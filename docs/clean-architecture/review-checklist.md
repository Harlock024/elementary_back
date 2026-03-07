## Checklist de revisión arquitectónica

- [ ] La lógica de negocio del workflow vive en `application/use_cases`.
- [ ] `domain` no importa Django, DRF ni modelos ORM.
- [ ] Las vistas HTTP delegan en un caso de uso (sin orquestación de negocio compleja).
- [ ] El acceso a datos se realiza por un adaptador de `infrastructure` que implementa un puerto.
- [ ] El endpoint mantiene ruta, método y formato de respuesta esperado.
- [ ] Existen pruebas unitarias de caso de uso y pruebas de endpoint para el workflow migrado.
- [ ] Se removió lógica duplicada legado del workflow migrado.

## Endpoints migrados (marzo 2026)

- `students`: `PUT /api/students/<id>/`, `PATCH /api/students/<id>/`, `DELETE /api/students/<id>/`
- `staff`: `PUT /api/staff/<id>/`, `DELETE /api/staff/<id>/`
- `academics` (school-grades): `PUT /api/academics/school-grades/<id>/`, `PATCH /api/academics/school-grades/<id>/`
- `academics` (group): `PUT /api/academics/groups/<id>/`, `PATCH /api/academics/groups/<id>/`
- `academics` (subject): `PUT /api/academics/subjects/<id>/`, `PATCH /api/academics/subjects/<id>/`
- `academics` (enrollment): `PUT /api/academics/enrollments/<id>/`, `PATCH /api/academics/enrollments/<id>/`
- `academics` (classroom): `PUT /api/academics/classrooms/<id>/`, `PATCH /api/academics/classrooms/<id>/`, `DELETE /api/academics/classrooms/<id>/`
- `grades`: `PUT /api/grades/<id>/`, `DELETE /api/grades/<id>/`
- `attendance`: `PATCH /api/attendances/<id>/`
