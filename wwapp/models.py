# import django
from django.core import exceptions
# from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models, IntegrityError
# from django.contrib.auth import get_user_model
from django.conf import settings

# get the auth user_model and assign it
User = settings.AUTH_USER_MODEL


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(unique=True, max_length=45)
    category_creator = models.ForeignKey(User, on_delete=models.PROTECT)
    category_description = models.CharField(null=True, max_length=300)

    class CategoryType(models.TextChoices):
        PROJECT = 'PROJECT', _('Project')
        TOPIC = 'TOPIC', _('Topic')
        SUBTOPIC = 'SUBTOPIC', _('SubTopic')

    category_type = models.CharField(max_length=45, choices=CategoryType.choices, default=CategoryType.PROJECT)

    class Meta:
        verbose_name_plural = 'Categories'
        indexes = [
            models.Index(fields=['category_name']),
        ]

    # def is_project(self):
    #     return self.category_type == self.CategoryType.PROJECT

    #
    #     # TODO use manager class instead
    #     @staticmethod
    #     def get_root_categories():
    #         return Category.objects.filter(category_type=Category.CategoryType.PROJECT)
    #
    def save(self, *args, **kwargs):
        # save to create id
        super().save(*args, **kwargs)
        # create new category item and save
        # TODO validate selected parent_category is valid (must be PROJECT or TOPIC )
        if (self.category_type is Category.CategoryType.TOPIC) or (
                self.category_type is Category.CategoryType.SUBTOPIC):
            # print(f"cat type: {self.category_type} is TOPIC or SUBTOPIC")
            try:
                CategoryItem.objects.get(item_category=self)
                # print(f"No new item was saved the item already exists:\n"
                #       f" - id: {self.category_id}")
            except exceptions.ObjectDoesNotExist:
                i = CategoryItem(item_category=self)
                i.save()
                # print(f"Category.save()/new CategoryItem created and saved{i.__str__()}")
        else:
            # print(f"Category.save()/No CategoryItem was created since Category is a PROJECT")
            # check to delete any CategoryItems that may exist
            try:
                CategoryItem.objects.get(item_category=self).delete()
                # print(f"Deleting Corresponding CategoryItem:\n"
                #       f" - id: {self.category_id}")
            except exceptions.ObjectDoesNotExist:
                pass
        # super().save(*args, **kwargs)

    def __str__(self):
        # parent_cat_name = "Null"
        try:
            i = CategoryItem.objects.get(item_category_id=self.category_id)
            a = CategoryItemAssignation.objects.get(item_id=i.item_id)
            Category.objects.get(category_id=a.parent_category_id)
            parent_cat_name = Category.objects.get(category_id=a.parent_category_id).category_name
        except exceptions.ObjectDoesNotExist:
            parent_cat_name = "Null"

        output = f" - Category Name:{self.category_name} " \
                 f"\n - Type:{self.category_type} " \
                 f"\n - Parent: {parent_cat_name} " \
                 f"\n - By: {self.category_creator}"
        return output


class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    article_title = models.CharField(max_length=45)
    pub_date = models.DateTimeField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    published = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    # creation_date = models.DateTimeField(default=timezone.now)
    article_parent = models.ForeignKey("Article", on_delete=models.SET_NULL, null=True, blank=True)

    # visits = models.IntegerField(default=0) TODO make 1*n table storing ip of each visitor and article id
    """
    # populate with -  default=timezone.now - from django.utils.timezone.now()
    # edit_date = models.DateField(auto_now=True)
    # can be used instead auto_now_add = True,
    """

    class Meta:
        indexes = [
            models.Index(fields=['article_title']),
            models.Index(fields=['author']),
        ]

    def save(self, *args, **kwargs):
        # check if CategoryItem already exists
        try:
            if self.article_id is None:
                raise exceptions.ObjectDoesNotExist
            i = CategoryItem.objects.get(item_article_id=self.article_id)
            if self.published:
                try:
                    a = CategoryItemAssignation.objects.get(item_id=i.item_id)
                    Category.objects.get(category_id=a.parent_category_id)
                except exceptions.ObjectDoesNotExist:
                    raise IntegrityError("The Article cannot be published without a parent Category")
            # if exists no changes need to be made to CategoryItem, just save Article
            super().save()
        except exceptions.ObjectDoesNotExist:
            # create new category item and save
            if not self.published:
                super().save()
                a = self.article_id
                # v =
                ArticleVersion(article_id=self.article_id).save()
                # ArticleVersion.objects.create(article_id=self.article_id)
                # i =
                CategoryItem.objects.create(item_article_id=self.article_id)
            else:
                raise exceptions.ValidationError("The Article cannot be published without CategoryItem")
        except IntegrityError:
            raise IntegrityError("The Article cannot be published without a parent Category")

    def __str__(self):
        output = f"\n - ID: {self.article_id}" \
                 f"\n - Title: {self.article_title}" \
                 f"\n - By: {self.author.username}"
        return output


class ArticleVersion(models.Model):
    article_version_id = models.AutoField(primary_key=True)
    edit_date = models.DateTimeField(default=timezone.now)
    version = models.IntegerField(default=1, null=False)
    article = models.ForeignKey(Article, null=False, blank=False, on_delete=models.CASCADE)
    secret_note = models.TextField(null=True, blank=True)
    # secret_notes = models.BaseEncryptedField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['article', 'version'], name="article_version_unique", )
        ]

    def save(self, *args, **kwargs):
        # TODO for later: make new version when saving instead of only keeping the first
        #  ** only new versions should be saved. old versions should not be overridden
        #  for now: Only one version will be stored (Version 1) and overridden
        # try:
        #     # self.file_name = f'{self.article_id}_{self.version}'
        #     versions = ArticleVersion.objects.filter(article_id=self.article_id).order_by('version')
        #     # check if content is different from last version
        #     # last_ver = versions[-1]
        #     # if last_ver != current session
        #     self.version = len(versions) + 1
        #     super().save(*args, **kwargs)
        #     # else
        #     # do nothing
        # except exceptions.EmptyResultSet:
        #     self.version = 1
        #     super().save(*args, **kwargs)
        super().save(*args, **kwargs)


class CategoryItem(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_article = models.OneToOneField(Article, on_delete=models.CASCADE, null=True, blank=True)
    item_category = models.OneToOneField(Category, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.item_article_id is not None:
            a = Article.objects.get(article_id=self.item_article_id)
            return f"Item Article {a.__str__()}"
        else:
            c = Category.objects.get(category_id=self.item_category_id)
            return f"Item Category {c.__str__()}"

    def save(self, *args, **kwargs):
        if (self.item_article_id is None and self.item_category_id is not None) or \
                (self.item_category_id is None and self.item_article_id is not None):
            print(f"saved new CategoryItem:"
                  f"\n - article id:{self.item_article_id}"
                  f"\n - category id:{self.item_category_id}")
            super().save(*args, **kwargs)
        else:
            # print("an article or category must be selected")
            raise ValueError("an article or category must be selected")


class CategoryItemAssignation(models.Model):
    item_assignation_id = models.AutoField(primary_key=True)
    parent_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    item = models.OneToOneField(CategoryItem, on_delete=models.CASCADE, null=False, blank=False, unique=True)
    position = models.IntegerField(null=False, blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['parent_category', 'position'], name="parent_category_position_unique", )
        ]

    def __str__(self):
        return f"- Position: {self.position} " \
               f"- Parent Category: {self.parent_category.category_name} || " \
               f"- Item: {self.item.__str__()}"


class Image(models.Model):
    image_id = models.AutoField(primary_key=True)
    image_name = models.CharField(max_length=45, unique=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    image_owner = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    public = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.image_id} - {self.upload_date} - {self.image_name}  " \
               f"Uploaded by {self.image_owner.username} - {self.description}"


class ImgurImage(Image):
    """
    stores the details of images that are uploaded to imgur
    *in future could include embedded images
    """
    imgur_image_id = models.AutoField(primary_key=True)
    url = models.URLField(blank=False, null=False)

    def __str__(self):
        output = f" {self.imgur_image_id} - {super().__str__()}"
        return output


class S3Image(Image):
    """
    This class is used to store images that are accessed frequently
    like site background and stored in S3 storage
    """
    s3_image_id = models.AutoField(primary_key=True)

    def get_upload_path(instance, filename) -> str:
        return f'images/uploads/{instance.image_owner.id}/{filename}'

    location = models.ImageField(upload_to=get_upload_path)

    def __str__(self):
        output = f" {self.s3_image_id} - {super().__str__()}"
        return output


class CategoryEditor(models.Model):
    category_editor_id = models.AutoField(primary_key=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
    )
    editor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['category', 'editor'], name="category_editor_unique", )
        ]

    def __str__(self):
        category = Category.objects.get(category_id=self.category_id)
        editor = User.objects.get(user_id=self.editor_id)

        output = f"Category\n{category.__str__()}" \
                 f"Editor\n{editor.__str__()}"
        return output


class ArticleEditor(models.Model):
    article_editor_id = models.AutoField(primary_key=True)
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
    )
    editor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['article', 'editor'], name="article_editor_unique", )
        ]

    def __str__(self):
        article = Article.objects.get(article_id=self.article_id)
        editor = User.objects.get(user_id=self.editor_id)

        output = f"Article\n{article.__str__()}" \
                 f"Editor\n{editor.__str__()}"
        return output
