import datetime
import re
import uuid

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q


def _dates_for_name(name):
    match = re.fullmatch(r"(\d{4})-(\d{4})", name or "")
    if match:
        first, second = map(int, match.groups())
        return datetime.date(first, 8, 1), datetime.date(second, 7, 31)
    match = re.fullmatch(r"\d{4}", name or "")
    if match:
        year = int(name)
        return datetime.date(year, 1, 1), datetime.date(year, 12, 31)
    return datetime.date(2000, 1, 1), datetime.date(2099, 12, 31)


def _period_for_date(periods, value, fallback):
    if value:
        for period in periods:
            if period.start_date <= value <= period.end_date:
                return period
        return min(
            periods,
            key=lambda period: min(
                abs((value - period.start_date).days),
                abs((value - period.end_date).days),
            ),
        )
    return fallback


def populate_periods(apps, schema_editor):
    AcademicPeriod = apps.get_model("academics", "AcademicPeriod")
    Enrollment = apps.get_model("academics", "Enrollment")
    ClassRoom = apps.get_model("academics", "ClassRoom")
    Assignment = apps.get_model("assignments", "Assignment")
    Attendance = apps.get_model("attendance", "Attendance")
    GradingCriteria = apps.get_model("grades", "GradingCriteria")
    StudentGrade = apps.get_model("grades", "StudentGrade")

    names = list(
        Enrollment.objects.exclude(period="")
        .values_list("period", flat=True)
        .distinct()
    )
    if not names:
        today = datetime.date.today()
        year = today.year if today.month >= 8 else today.year - 1
        names = [f"{year}-{year + 1}"]

    periods = []
    for name in names:
        start_date, end_date = _dates_for_name(name)
        periods.append(
            AcademicPeriod.objects.create(
                name=name,
                start_date=start_date,
                end_date=end_date,
                status="draft",
            )
        )
    periods.sort(key=lambda item: (item.start_date, item.end_date))
    active_period = periods[-1]
    AcademicPeriod.objects.exclude(pk=active_period.pk).update(status="closed")
    AcademicPeriod.objects.filter(pk=active_period.pk).update(status="active")
    active_period.status = "active"

    periods_by_name = {period.name: period for period in periods}
    for enrollment in Enrollment.objects.all().iterator():
        enrollment.academic_period_id = periods_by_name.get(
            enrollment.period, active_period
        ).pk
        enrollment.save(update_fields=["academic_period"])

    for original in list(ClassRoom.objects.all()):
        relevant_ids = set(
            Enrollment.objects.filter(group_id=original.group_id)
            .values_list("academic_period_id", flat=True)
            .distinct()
        )
        if not relevant_ids:
            relevant_ids = {active_period.pk}
        relevant = [period for period in periods if period.pk in relevant_ids]
        keeper_period = max(relevant, key=lambda item: item.end_date)
        original.academic_period_id = keeper_period.pk
        original.save(update_fields=["academic_period"])

        classrooms = {keeper_period.pk: original}
        for period in relevant:
            if period.pk == keeper_period.pk:
                continue
            classrooms[period.pk] = ClassRoom.objects.create(
                id=uuid.uuid4(),
                staff_id=original.staff_id,
                group_id=original.group_id,
                academic_period_id=period.pk,
            )

        for attendance in Attendance.objects.filter(class_room_id=original.pk):
            period = _period_for_date(relevant, attendance.date, keeper_period)
            attendance.class_room_id = classrooms[period.pk].pk
            attendance.save(update_fields=["class_room"])

        criteria_cache = {}
        for assignment in Assignment.objects.filter(class_room_id=original.pk):
            period = _period_for_date(relevant, assignment.due_date, keeper_period)
            target = classrooms[period.pk]
            criteria = GradingCriteria.objects.get(pk=assignment.grading_criteria_id)
            if target.pk != original.pk:
                cache_key = (criteria.pk, target.pk)
                cloned = criteria_cache.get(cache_key)
                if cloned is None:
                    cloned = GradingCriteria.objects.create(
                        id=uuid.uuid4(),
                        name=criteria.name,
                        class_room_id=target.pk,
                        percentage=criteria.percentage,
                        is_attendance_based=criteria.is_attendance_based,
                    )
                    criteria_cache[cache_key] = cloned
                assignment.grading_criteria_id = cloned.pk
            assignment.class_room_id = target.pk
            assignment.save(update_fields=["class_room", "grading_criteria"])

    for grade in StudentGrade.objects.select_related("assignment").all():
        grade.class_room_id = grade.assignment.class_room_id
        grade.save(update_fields=["class_room"])


def merge_periods(apps, schema_editor):
    Enrollment = apps.get_model("academics", "Enrollment")
    ClassRoom = apps.get_model("academics", "ClassRoom")
    Assignment = apps.get_model("assignments", "Assignment")
    Attendance = apps.get_model("attendance", "Attendance")
    GradingCriteria = apps.get_model("grades", "GradingCriteria")
    StudentGrade = apps.get_model("grades", "StudentGrade")

    for group_id in ClassRoom.objects.values_list("group_id", flat=True).distinct():
        classrooms = list(
            ClassRoom.objects.filter(group_id=group_id).order_by("created_at", "pk")
        )
        if not classrooms:
            continue
        keeper = classrooms[0]
        clone_ids = [classroom.pk for classroom in classrooms[1:]]
        if not clone_ids:
            continue
        Attendance.objects.filter(class_room_id__in=clone_ids).update(
            class_room_id=keeper.pk
        )
        Assignment.objects.filter(class_room_id__in=clone_ids).update(
            class_room_id=keeper.pk
        )
        StudentGrade.objects.filter(class_room_id__in=clone_ids).update(
            class_room_id=keeper.pk
        )
        GradingCriteria.objects.filter(class_room_id__in=clone_ids).update(
            class_room_id=keeper.pk
        )
        ClassRoom.objects.filter(pk__in=clone_ids).delete()
    Enrollment.objects.update(academic_period_id=None)
    ClassRoom.objects.update(academic_period_id=None)


def drop_legacy_enrollment_unique(apps, schema_editor):
    Enrollment = apps.get_model("academics", "Enrollment")
    table = Enrollment._meta.db_table
    constraints = schema_editor.connection.introspection.get_constraints(
        schema_editor.connection.cursor(), table
    )
    expected = {"student_id", "period", "group_id"}
    for name, details in constraints.items():
        if details.get("unique") and set(details.get("columns", [])) == expected:
            if details.get("index"):
                schema_editor.execute(
                    "DROP INDEX IF EXISTS %s" % schema_editor.quote_name(name)
                )
            else:
                schema_editor.execute(
                    "ALTER TABLE %s DROP CONSTRAINT IF EXISTS %s"
                    % (schema_editor.quote_name(table), schema_editor.quote_name(name))
                )


def restore_legacy_enrollment_unique(apps, schema_editor):
    Enrollment = apps.get_model("academics", "Enrollment")
    table = schema_editor.quote_name(Enrollment._meta.db_table)
    schema_editor.execute(
        "ALTER TABLE %s ADD CONSTRAINT %s UNIQUE (student_id, period, group_id)"
        % (table, schema_editor.quote_name("uniq_student_legacy_period_group"))
    )


class Migration(migrations.Migration):
    dependencies = [
        ("academics", "0006_protect_academic_history_and_unique_classrooms"),
        ("assignments", "0003_protect_assignment_history"),
        ("attendance", "0003_protect_attendance_history"),
        ("grades", "0003_protect_grading_history"),
    ]

    operations = [
        migrations.CreateModel(
            name="AcademicPeriod",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=20, unique=True)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("status", models.CharField(choices=[("draft", "Borrador"), ("active", "Activo"), ("closed", "Cerrado")], default="draft", max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "academic_periods", "ordering": ["-start_date"]},
        ),
        migrations.AddConstraint(
            model_name="academicperiod",
            constraint=models.CheckConstraint(condition=Q(start_date__lt=models.F("end_date")), name="academic_period_dates_ordered"),
        ),
        migrations.AddConstraint(
            model_name="academicperiod",
            constraint=models.UniqueConstraint(condition=Q(status="active"), fields=("status",), name="uniq_active_academic_period"),
        ),
        migrations.AddField(
            model_name="enrollment",
            name="academic_period",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name="enrollments", to="academics.academicperiod"),
        ),
        migrations.AddField(
            model_name="classroom",
            name="academic_period",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name="classrooms", to="academics.academicperiod"),
        ),
        migrations.RemoveConstraint(model_name="classroom", name="uniq_classroom_group"),
        migrations.RunPython(populate_periods, merge_periods),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    drop_legacy_enrollment_unique,
                    restore_legacy_enrollment_unique,
                )
            ],
            state_operations=[
                migrations.AlterUniqueTogether(
                    name="enrollment",
                    unique_together=set(),
                )
            ],
        ),
        migrations.AlterField(
            model_name="enrollment",
            name="academic_period",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="enrollments", to="academics.academicperiod"),
        ),
        migrations.AlterField(
            model_name="classroom",
            name="academic_period",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="classrooms", to="academics.academicperiod"),
        ),
        migrations.AddConstraint(
            model_name="enrollment",
            constraint=models.UniqueConstraint(fields=("student", "academic_period", "group"), name="uniq_student_period_group"),
        ),
        migrations.AddConstraint(
            model_name="classroom",
            constraint=models.UniqueConstraint(fields=("group", "academic_period"), name="uniq_classroom_group_period"),
        ),
    ]
