# Generated by Django 3.1.5 on 2021-01-22 11:14

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('wwapp', '0003_auto_20210121_1652'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='articleversion',
            name='location',
        ),
        migrations.AddField(
            model_name='articleversion',
            name='content',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='upload_date',
            field=models.DateTimeField(default=datetime.datetime(2021, 1, 22, 11, 14, 58, 969764, tzinfo=utc), editable=False),
        ),
        migrations.CreateModel(
            name='CategoryItemAssignation',
            fields=[
                ('item_assignation_id', models.AutoField(primary_key=True, serialize=False)),
                ('position', models.IntegerField()),
                ('item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='wwapp.categoryitem')),
                ('parent_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wwapp.category')),
            ],
        ),
        migrations.AddConstraint(
            model_name='categoryitemassignation',
            constraint=models.UniqueConstraint(fields=('parent_category', 'position'), name='parent_category_position_unique'),
        ),
    ]