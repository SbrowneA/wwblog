# Generated by Django 3.1.5 on 2021-02-11 03:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wwapp', '0004_articleversion_hidden_notes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories'},
        ),
        migrations.RenameField(
            model_name='articleversion',
            old_name='hidden_notes',
            new_name='secret_note',
        ),
    ]