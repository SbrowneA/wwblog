# Generated by Django 3.1.5 on 2021-02-20 09:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('article_id', models.AutoField(primary_key=True, serialize=False)),
                ('article_title', models.CharField(max_length=45)),
                ('pub_date', models.DateTimeField(blank=True, null=True)),
                ('published', models.BooleanField(default=False)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('article_parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='wwapp.article')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('category_id', models.AutoField(primary_key=True, serialize=False)),
                ('category_name', models.CharField(max_length=45, unique=True)),
                ('category_type', models.CharField(choices=[('PROJECT', 'Project'), ('TOPIC', 'Topic'), ('SUBTOPIC', 'SubTopic')], default='PROJECT', max_length=45)),
                ('category_creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
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
                ('editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ArticleVersion',
            fields=[
                ('article_version_id', models.AutoField(primary_key=True, serialize=False)),
                ('edit_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('version', models.IntegerField(default=1)),
                ('secret_note', models.TextField(blank=True, null=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wwapp.article')),
            ],
        ),
        migrations.CreateModel(
            name='ArticleEditor',
            fields=[
                ('article_editor_id', models.AutoField(primary_key=True, serialize=False)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wwapp.article')),
                ('editor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
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
            model_name='articleversion',
            constraint=models.UniqueConstraint(fields=('article', 'version'), name='article_version_unique'),
        ),
        migrations.AddConstraint(
            model_name='articleeditor',
            constraint=models.UniqueConstraint(fields=('article', 'editor'), name='article_editor_unique'),
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['article_title'], name='wwapp_artic_article_419a0b_idx'),
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['author'], name='wwapp_artic_author__2096fd_idx'),
        ),
    ]
