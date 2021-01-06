# Generated by Django 3.1.4 on 2021-01-06 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wwapp', '0008_categoryitemassignation'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='categoryitemassignation',
            constraint=models.UniqueConstraint(fields=('parent_category', 'position'), name='parent_category_position_unique'),
        ),
    ]
