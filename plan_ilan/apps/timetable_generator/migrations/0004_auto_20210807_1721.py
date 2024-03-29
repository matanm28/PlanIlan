# Generated by Django 3.2 on 2021-08-07 14:21

from django.db import migrations, models
import django.db.models.deletion
import plan_ilan.apps.timetable_generator.models.timetable


class Migration(migrations.Migration):

    dependencies = [
        ('timetable_generator', '0003_auto_20210618_1610'),
    ]

    operations = [
        migrations.AddField(
            model_name='timetable',
            name='is_done',
            field=models.BooleanField(default=False, null=True),
        ),
        migrations.AddField(
            model_name='timetablesolution',
            name='possibly_invalid',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='elective_points_bound',
            field=models.ForeignKey(default=plan_ilan.apps.timetable_generator.models.timetable.get_default_elective_points_bound, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='timetables', to='timetable_generator.interval'),
        ),
    ]
