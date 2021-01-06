# Generated by Django 3.1.4 on 2021-01-06 15:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wwapp', '0004_auto_20210107_0203'),
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
    ]
