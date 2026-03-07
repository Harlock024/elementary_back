## 1. Módulo Students - Completar CRUD

- [x] 1.1 Crear `UpdateStudentCommand` en `students/application/dto/`
- [x] 1.2 Crear `update_student.py` use case en `students/application/use_cases/`
- [x] 1.3 Crear `delete_student.py` use case en `students/application/use_cases/`
- [x] 1.4 Extender `StudentRepository` port con métodos `update()` y `delete()`
- [x] 1.5 Implementar `update()` y `delete()` en `DjangoStudentRepository`
- [x] 1.6 Crear factory functions para update/delete use cases
- [x] 1.7 Refactorizar `StudentViewSet.put()` para usar update use case
- [x] 1.8 Refactorizar `StudentViewSet.patch()` para usar update use case
- [x] 1.9 Refactorizar `StudentViewSet.delete()` para usar delete use case
- [x] 1.10 Eliminar imports directos de `Student` model en views
- [x] 1.11 Agregar tests unitarios para update/delete use cases
- [x] 1.12 Agregar smoke tests para PUT/PATCH/DELETE endpoints

## 2. Módulo Staff - Completar CRUD

- [x] 2.1 Crear `UpdateStaffCommand` en `staff/application/dto/`
- [x] 2.2 Crear `update_staff.py` use case en `staff/application/use_cases/`
- [x] 2.3 Crear `delete_staff.py` use case en `staff/application/use_cases/`
- [x] 2.4 Extender `StaffRepository` port con métodos `update()` y `delete()`
- [x] 2.5 Implementar `update()` y `delete()` en `DjangoStaffRepository`
- [x] 2.6 Crear factory functions para update/delete use cases
- [x] 2.7 Refactorizar `StaffView.put()` para usar update use case
- [x] 2.8 Refactorizar `StaffView.delete()` para usar delete use case
- [x] 2.9 Eliminar imports directos de `Staff` model en views (excepto auth)
- [x] 2.10 Agregar tests unitarios para update/delete use cases
- [x] 2.11 Agregar smoke tests para PUT/DELETE endpoints

## 3. Módulo Academics - Completar CRUD (SchoolGrade)

- [x] 3.1 Crear `UpdateSchoolGradeCommand` en `academics/application/dto/`
- [x] 3.2 Crear `update_school_grade.py` use case
- [x] 3.3 Extender `SchoolGradeRepository` port con método `update()`
- [x] 3.4 Implementar `update()` en `DjangoSchoolGradeRepository`
- [x] 3.5 Refactorizar `SchoolGradeViewSet.put()` y `patch()` para usar update use case
- [x] 3.6 Agregar tests para SchoolGrade update use case

## 4. Módulo Academics - Completar CRUD (Group, Subject, ClassRoom, Enrollment)

- [x] 4.1 Crear use cases de update para Group, Subject, ClassRoom, Enrollment
- [x] 4.2 Crear DTOs de comando para cada entidad
- [x] 4.3 Extender repository ports existentes o crear nuevos
- [x] 4.4 Implementar adaptadores Django para cada repositorio
- [x] 4.5 Refactorizar views para delegar a use cases
- [x] 4.6 Eliminar acceso directo a modelos en `academics/views.py`
- [x] 4.7 Agregar tests unitarios para use cases de academics
- [x] 4.8 Agregar smoke tests para endpoints migrados

## 5. Módulo Grades - Completar CRUD

- [x] 5.1 Crear `UpdateGradeCommand` en `grades/application/dto/`
- [x] 5.2 Crear `update_grade.py` use case
- [x] 5.3 Crear `delete_grade.py` use case
- [x] 5.4 Extender `GradeRepository` port con métodos `update()` y `delete()`
- [x] 5.5 Implementar `update()` y `delete()` en `DjangoGradeRepository`
- [x] 5.6 Refactorizar `GradeViewSet.put()` para usar update use case
- [x] 5.7 Eliminar imports directos de `StudentGrade` model en views
- [x] 5.8 Agregar tests unitarios para update/delete use cases
- [x] 5.9 Agregar smoke tests para PUT endpoint

## 6. Módulo Attendance - Completar CRUD

- [x] 6.1 Crear `UpdateAttendanceCommand` en `attendance/application/dto/`
- [x] 6.2 Crear `update_attendance.py` use case
- [x] 6.3 Extender `AttendanceRepository` port con método `update()`
- [x] 6.4 Implementar `update()` en `DjangoAttendanceRepository`
- [x] 6.5 Refactorizar `AttendaceView.patch()` para usar update use case
- [x] 6.6 Eliminar imports directos de `Attendance` model en views
- [x] 6.7 Agregar tests unitarios para update use case
- [x] 6.8 Agregar smoke tests para PATCH endpoint

## 7. Validación Final y Documentación

- [x] 7.1 Verificar que los workflows CRUD migrados no tengan acceso directo a ORM en `views.py`
- [x] 7.2 Ejecutar suite completa de tests
- [x] 7.3 Actualizar `docs/clean-architecture/review-checklist.md` con endpoints migrados
- [x] 7.4 Documentar completion status por módulo
