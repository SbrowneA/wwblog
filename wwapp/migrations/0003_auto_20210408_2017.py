# Generated by Django 3.1.7 on 2021-04-08 10:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import wwapp.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wwapp', '0002_category_category_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('image_id', models.AutoField(primary_key=True, serialize=False)),
                ('image_name', models.CharField(max_length=45, unique=True)),
                ('description', models.CharField(blank=True, max_length=100, null=True)),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('public', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['author_id', 'published', '-pub_date'], name='wwapp_artic_author__124596_idx'),
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['published', '-pub_date'], name='wwapp_artic_publish_88082a_idx'),
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['published', 'pub_date'], name='wwapp_artic_publish_7d57f5_idx'),
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['author_id', 'published', '-creation_date'], name='wwapp_artic_author__61eddd_idx'),
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['author_id', 'published', 'creation_date'], name='wwapp_artic_author__5f1232_idx'),
        ),
        migrations.AddIndex(
            model_name='articleversion',
            index=models.Index(fields=['article_id', 'version'], name='wwapp_artic_article_c3acbf_idx'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['category_creator_id', 'category_type', 'category_name'], name='wwapp_categ_categor_06a7cb_idx'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['category_type', 'category_name'], name='wwapp_categ_categor_213194_idx'),
        ),
        migrations.AddIndex(
            model_name='categoryitemassignation',
            index=models.Index(fields=['position'], name='wwapp_categ_positio_2fd119_idx'),
        ),
        migrations.AddIndex(
            model_name='categoryitemassignation',
            index=models.Index(fields=['parent_category_id', 'position'], name='wwapp_categ_parent__cc7400_idx'),
        ),
        migrations.CreateModel(
            name='ImgurImage',
            fields=[
                ('image_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='wwapp.image')),
                ('imgur_image_id', models.AutoField(primary_key=True, serialize=False)),
                ('url', models.URLField()),
            ],
            bases=('wwapp.image',),
        ),
        migrations.CreateModel(
            name='S3Image',
            fields=[
                ('image_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to='wwapp.image')),
                ('s3_image_id', models.AutoField(primary_key=True, serialize=False)),
                ('location', models.ImageField(upload_to=wwapp.models.S3Image.get_upload_path)),
            ],
            bases=('wwapp.image',),
        ),
        migrations.AddField(
            model_name='image',
            name='image_owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]