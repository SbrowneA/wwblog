# Generated by Django 3.1.4 on 2021-01-06 15:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wwapp', '0005_articleeditor'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryEditor',
            fields=[
                ('category_editor_id', models.AutoField(primary_key=True, serialize=False)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wwapp.category')),
                ('editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wwapp.user')),
            ],
        ),
        migrations.AddConstraint(
            model_name='categoryeditor',
            constraint=models.UniqueConstraint(fields=('category', 'editor'), name='category_editor_unique'),
        ),
    ]
