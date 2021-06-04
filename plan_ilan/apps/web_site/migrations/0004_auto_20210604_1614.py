# Generated by Django 3.2 on 2021-06-04 16:14

from django.db import migrations
import plan_ilan.costume_fields


class Migration(migrations.Migration):

    dependencies = [
        ('web_site', '0003_auto_20210531_1030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lessontime',
            name='end_time',
            field=plan_ilan.costume_fields.ImprovedTimeField(),
        ),
        migrations.AlterField(
            model_name='lessontime',
            name='start_time',
            field=plan_ilan.costume_fields.ImprovedTimeField(),
        ),
        migrations.AlterUniqueTogether(
            name='courserating',
            unique_together={('course', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='teacherrating',
            unique_together={('teacher', 'user')},
        ),
    ]
