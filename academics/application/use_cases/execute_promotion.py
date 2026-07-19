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
        from academics.models import AcademicPeriod, ClassRoom, Enrollment, Group, SchoolGrade

        with transaction.atomic():
            try:
                source_classroom = ClassRoom.objects.select_for_update().select_related(
                    'group', 'academic_period'
                ).get(
                    pk=command.source_classroom_id
                )
            except ClassRoom.DoesNotExist:
                raise PromotionError("Classroom de origen no encontrada")

            source_group = source_classroom.group
            source_period = source_classroom.academic_period
            if source_period.status != AcademicPeriod.Status.ACTIVE:
                raise PromotionError("Solo se puede promover desde el ciclo activo")
            needs_target_period = any(
                item.action in {'promote', 'repeat'} for item in command.students
            )
            target_period = None
            if needs_target_period:
                try:
                    lookup = (
                        {'pk': command.target_period_id}
                        if command.target_period_id
                        else {'name': command.period}
                    )
                    target_period = AcademicPeriod.objects.select_for_update().get(**lookup)
                except AcademicPeriod.DoesNotExist:
                    raise PromotionError("Ciclo académico destino no encontrado")
                if target_period.status == AcademicPeriod.Status.CLOSED:
                    raise PromotionError("El ciclo académico destino está cerrado")
                if target_period.start_date <= source_period.start_date:
                    raise PromotionError("El ciclo destino debe ser posterior al ciclo de origen")

            student_ids = [item.student_id for item in command.students]

            active_enrollments = {
                str(e.student_id): e
                for e in Enrollment.objects.select_related('student').filter(
                    student_id__in=student_ids,
                    group=source_group,
                    academic_period=source_period,
                    state__in=('activo', 'active'),
                ).select_for_update()
            }

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
                    academic_period=target_period,
                    defaults={'staff': source_classroom.staff},
                )

            repeat_classroom = None
            if any(item.action == 'repeat' for item in command.students):
                repeat_classroom, _ = ClassRoom.objects.get_or_create(
                    group=source_group,
                    academic_period=target_period,
                    defaults={'staff': source_classroom.staff},
                )

            counts = {'promote': 0, 'repeat': 0, 'graduate': 0}

            for item in command.students:
                enrollment = active_enrollments.get(item.student_id)
                if enrollment is None:
                    expected_group = target_group if item.action == 'promote' else source_group
                    already_done = (
                        item.action == 'graduate'
                        and Enrollment.objects.filter(
                            student_id=item.student_id,
                            group=source_group,
                            academic_period=source_period,
                            state='inactivo',
                        ).exists()
                    ) or (
                        item.action in {'promote', 'repeat'}
                        and Enrollment.objects.filter(
                            student_id=item.student_id,
                            group=expected_group,
                            academic_period=target_period,
                            state__in=('activo', 'active'),
                        ).exists()
                    )
                    if already_done:
                        counts[item.action] += 1
                        continue
                    raise PromotionError(
                        f"El alumno {item.student_id} no tiene inscripción activa en el ciclo de origen"
                    )

                student = enrollment.student

                enrollment.state = 'inactivo'
                enrollment.save(update_fields=['state'])

                if item.action == 'promote':
                    Enrollment.objects.create(
                        student=student,
                        group=target_group,
                        period=target_period.name,
                        academic_period=target_period,
                        state='activo',
                    )
                    counts['promote'] += 1

                elif item.action == 'repeat':
                    Enrollment.objects.create(
                        student=student,
                        group=source_group,
                        period=target_period.name,
                        academic_period=target_period,
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
