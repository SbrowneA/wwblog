# Generated by Django 3.1.4 on 2021-01-05 03:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wwapp', '0010_auto_20210105_1357'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleEditor',
            fields=[
                ('article_editor_id', models.AutoField(primary_key=True, serialize=False)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wwapp.article')),
                ('editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wwapp.user')),
            ],
        ),
        migrations.AddConstraint(
            model_name='articleeditor',
            constraint=models.UniqueConstraint(fields=('article', 'editor'), name='article_editor_unique'),
        ),
    ]
