# Generated by Django 3.1.4 on 2021-01-18 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wwapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('category_id', models.AutoField(primary_key=True, serialize=False)),
                ('category_name', models.CharField(max_length=45, unique=True)),
                ('category_type', models.CharField(choices=[('PROJECT', 'Project'), ('TOPIC', 'Topic'), ('SUBTOPIC', 'SubTopic')], default='PROJECT', max_length=45)),
                ('category_creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='wwapp.user')),
            ],
        ),
        migrations.CreateModel(
            name='CategoryItem',
            fields=[
                ('item_id', models.AutoField(primary_key=True, serialize=False)),
                ('item_article', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wwapp.article')),
                ('item_category', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='wwapp.category')),
            ],
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
        migrations.CreateModel(
            name='CategoryEditor',
            fields=[
                ('category_editor_id', models.AutoField(primary_key=True, serialize=False)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wwapp.category')),
                ('editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wwapp.user')),
            ],
        ),
        migrations.CreateModel(
            name='ArticleEditor',
            fields=[
                ('article_editor_id', models.AutoField(primary_key=True, serialize=False)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wwapp.article')),
                ('editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wwapp.user')),
            ],
        ),
        migrations.AddConstraint(
            model_name='categoryitemassignation',
            constraint=models.UniqueConstraint(fields=('parent_category', 'position'), name='parent_category_position_unique'),
        ),
        migrations.AddConstraint(
            model_name='categoryeditor',
            constraint=models.UniqueConstraint(fields=('category', 'editor'), name='category_editor_unique'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['category_name'], name='wwapp_categ_categor_c92d4c_idx'),
        ),
        migrations.AddConstraint(
            model_name='articleeditor',
            constraint=models.UniqueConstraint(fields=('article', 'editor'), name='article_editor_unique'),
        ),
    ]
