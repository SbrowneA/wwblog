# Generated by Django 3.1.4 on 2021-01-07 07:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wwapp', '0011_auto_20210107_1735'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='category',
        ),
    ]
