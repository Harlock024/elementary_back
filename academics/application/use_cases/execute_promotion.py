from django.db import IntegrityError, transaction

from academics.application.dto.academics_dto import PromoteStudentsCommand
from academics.domain.exceptions.academics_exceptions import PromotionError


class ExecutePromotionUseCase:
    def execute(self, command: PromoteStudentsCommand) -> dict:
        try:
            return self._execute(command)
        except IntegrityError as exc:
            raise PromotionError(
                "La promoción entra en conflicto con una inscripción o estructura académica existente."
            ) from exc

    def _execute(self, command: PromoteStudentsCommand) -> dict:
        from academics.models import ClassRoom, Enrollment, Group, SchoolGrade

        with transaction.atomic():
            try:
                source_classroom = ClassRoom.objects.select_related('group').get(
                    pk=command.source_classroom_id
                )
            except ClassRoom.DoesNotExist:
                raise PromotionError("Classroom de origen no encontrada")

            source_group = source_classroom.group
            student_ids = [item.student_id for item in command.students]

            active_enrollments = {
                str(e.student_id): e
                for e in Enrollment.objects.select_related('student').filter(
                    student_id__in=student_ids,
                    group=source_group,
                    state='activo',
                ).select_for_update()
            }

            missing = [sid for sid in student_ids if sid not in active_enrollments]
            if missing:
                raise PromotionError(
                    f"Los siguientes alumnos no pertenecen al classroom de origen o no tienen inscripción activa: {missing}"
                )

            has_promotes = any(item.action == 'promote' for item in command.students)
            target_group = None
            target_classroom = None

            if has_promotes:
                try:
                    school_grade = SchoolGrade.objects.get(pk=command.target_group.school_grade_id)
                except SchoolGrade.DoesNotExist:
                    raise PromotionError("Grado escolar destino no encontrado")

                target_group, _ = Group.objects.get_or_create(
                    school_grade=school_grade,
                    letter=command.target_group.letter,
                )
                target_classroom, _ = ClassRoom.objects.get_or_create(
                    group=target_group,
                    defaults={'staff': source_classroom.staff},
                )

            counts = {'promote': 0, 'repeat': 0, 'graduate': 0}

            for item in command.students:
                enrollment = active_enrollments[item.student_id]
                student = enrollment.student

                enrollment.state = 'inactivo'
                enrollment.save(update_fields=['state'])

                if item.action == 'promote':
                    Enrollment.objects.create(
                        student=student,
                        group=target_group,
                        period=command.period,
                        state='activo',
                    )
                    counts['promote'] += 1

                elif item.action == 'repeat':
                    Enrollment.objects.create(
                        student=student,
                        group=source_group,
                        period=command.period,
                        state='activo',
                    )
                    counts['repeat'] += 1

                elif item.action == 'graduate':
                    student.state = 'inactivo'
                    student.save(update_fields=['state'])
                    counts['graduate'] += 1

            # El aula y el grupo de origen son parte del historial académico y
            # deben conservarse después de cerrar sus inscripciones activas.
            return {
                'promoted': counts['promote'],
                'repeated': counts['repeat'],
                'graduated': counts['graduate'],
                'target_group_id': str(target_group.id) if target_group else None,
                'target_classroom_id': str(target_classroom.id) if target_classroom else None,
            }
