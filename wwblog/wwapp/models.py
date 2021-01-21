import django
from django.core import exceptions
from django.shortcuts import get_object_or_404
# from django.core import exceptions as djangoex
# from django.utils import timezone
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True, null=False)
    username = models.CharField(max_length=14, null=False, blank=False)

    class Meta:
        indexes = [
            models.Index(fields=['username'])
        ]

    def __str__(self):
        output = f"User ID: {self.user_id}" \
                 f"Username: {self.username}"
        return output


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(unique=True, max_length=45)
    category_creator = models.ForeignKey(User, on_delete=models.PROTECT)

    class CategoryType(models.TextChoices):
        PROJECT = 'PROJECT', _('Project')
        TOPIC = 'TOPIC', _('Topic')
        SUBTOPIC = 'SUBTOPIC', _('SubTopic')

    category_type = models.CharField(max_length=45, choices=CategoryType.choices, default=CategoryType.PROJECT)

    class Meta:
        indexes = [
            models.Index(fields=['category_name']),
        ]

    def is_project(self):
        return self.category_type == self.CategoryType.PROJECT

    # TODO use manager class instead
    @staticmethod
    def get_root_categories():
        return Category.objects.filter(category_type=Category.CategoryType.PROJECT)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # create new category item and save
        # TODO validate selected parent_category is valid (must be PROJECT or TOPIC )
        if (self.category_type is Category.CategoryType.TOPIC) or (
                self.category_type is Category.CategoryType.SUBTOPIC):
            print(f"cat type: {self.category_type} is TOPIC or SUBTOPIC")
            try:
                CategoryItem.objects.get(item_category=self)
                print(f"No new item was saved the item already exists:\n"
                      f" - id: {self.category_id}")
            except exceptions.ObjectDoesNotExist:
                i = CategoryItem(item_category=self)
                i.save()
                print(f"Category.save()/new CategoryItem created and saved{i.__str__()}")
        else:
            print(f"Category.save()/No CategoryItem was created since Category is a PROJECT")
            # check to delete any CategoryItems that may exist
            try:
                CategoryItem.objects.get(item_category=self).delete()
                print(f"Deleting Corresponding CategoryItem:\n"
                      f" - id: {self.category_id}")
            except exceptions.ObjectDoesNotExist:
                pass

    def __str__(self):
        parent_cat_name = "Null"
        # try:
        #     i = CategoryItem.objects.get(item_category_id=self.category_id)
        #     a = CategoryItemAssignation.objects.get(item_id=i.item_id)
        #     Category.objects.get(category_id=a.parent_category_id)
        #     parent_cat_name = Category.objects.get(category_id=a.parent_category_id).category_name
        # except exceptions.ObjectDoesNotExist:
        #     parent_cat_name = "Null"

        output = f" - Category Name:{self.category_name} " \
                 f"\n - Type:{self.category_type} " \
                 f"\n - Parent: {parent_cat_name} " \
                 f"\n - By: {self.category_creator.username}"
        return output


class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    # TODO make id for table and article_no for reference
    # article_no = models.IntegerField(default=0)
    # TODO make new table called ArticleVersion(articleID, Version, previousArticleID)
    #  --where id is unique and previous version is unique
    article_title = models.CharField(max_length=45)
    pub_date = models.DateTimeField(blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    published = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    # creation_date = models.DateTimeField(default=timezone.now)
    # article_parent = models.ForeignKey("Article", on_delete=models.SET_DEFAULT, default=None, null=True, blank=True)

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

    # def save(self, *args, **kwargs):
    #     # check if CategoryItem already exists
    #     try:
    #         i = CategoryItem.objects.get(item_article_id=self.article_id)
    #         if self.published:
    #             try:
    #                 a = CategoryItemAssignation.objects.get(item_id=i.item_id)
    #                 parent = Category.objects.get(category_id=a.parent_category_id)
    #             except exceptions.ObjectDoesNotExist:
    #                 raise exceptions.ValidationError("The Article cannot be published without a parent Category")
    #         # if exists no changes need to be made to CategoryItem, just save Article
    #         super().save()
    #     except (exceptions.ObjectDoesNotExist, exceptions.ValidationError):
    #         # create new category item and save
    #         if not self.published:
    #             super().save()
    #             v = ArticleVersion(article_id=self.)
    #             i = CategoryItem(item_article_id=self.article_id)
    #             i.save()
    #         else:
    #             raise exceptions.ValidationError("The Article cannot be published without CategoryItem")

    def __str__(self):
        output = f"\n - ID: {self.article_id}" \
                 f"\n - Title: {self.article_title}" \
                 f"\n - By: {self.author.username}"
        # f"\n - Creation Date: {self.pub_date}"
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
    # placeholder_id = models.AutoField(primary_key=True)
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
        # DEPRECATED
        # unique_together = (('article_id', 'editor_id'),)

    def __str__(self):
        article = Article.objects.get(article_id=self.article_id)
        editor = User.objects.get(user_id=self.editor_id)

        output = f"Article\n{article.__str__()}" \
                 f"Editor\n{editor.__str__()}"
        return output


class ArticleVersion(models.Model):
    article_version_id = models.AutoField(primary_key=True)
    edit_date = models.DateTimeField(default=timezone.now)
    version = models.IntegerField(default=1, null=False)
    article = models.ForeignKey(Article, null=False, blank=False, on_delete=models.CASCADE)
    location = models.FileField(upload_to='posts/')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['article', 'version'], name="article_version_unique", )
        ]

    def save(self, *args, **kwargs):
        # ** only new versions should be saved. old versions should not be overridden
        try:
            self.file_name = f'{self.article_id}_{self.version}'
            versions = ArticleVersion.objects.filter(self.article_id).order_by('version')
            # check if content is different from last version
            last_ver = versions[-1]
            # if last_ver != current session
            self.version = len(versions) + 1
            super().save(*args, **kwargs)
            # else
            # do nothing
        except exceptions.EmptyResultSet:
            self.version = 1
            super().save(*args, **kwargs)

        pass


class CategoryItem(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_article = models.OneToOneField(Article, on_delete=models.CASCADE, null=True, blank=True)
    item_category = models.OneToOneField(Category, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.item_article_id is not None:
            a = Article.objects.get(article_id=self.item_article.article_id)
            return f"Article {a.__str__()}"
        else:
            c = Category.objects.get(category_id=self.item_category.category_id)
            return f"Category {c.__str__()}"

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


#
#
# class CategoryItemAssignation(models.Model):
#     item_assignation_id = models.AutoField(primary_key=True)
#     parent_category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     item = models.OneToOneField(CategoryItem, on_delete=models.CASCADE, null=False, blank=False, unique=True)
#     position = models.IntegerField(null=False, blank=False)
#
#     class Meta:
#         constraints = [
#             models.UniqueConstraint(fields=['parent_category', 'position'], name="parent_category_position_unique", )
#         ]
#
#     def __str__(self):
#         return f"- Position: {self.position} " \
#                f"- Parent Category: {self.parent_category.category_name} || " \
#                f"- Item: {self.item.__str__()}"


class ImageRemote(models.Model):
    """
    stores the details of images that are uploaded to imgur
    *in future could include embedded images
    """
    remote_image_id = models.AutoField(primary_key=True)
    image_owner = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    location = models.URLField(blank=False, null=False)

    def __str__(self):
        return f"Uploaded by {self.image_owner.username}"


class ImageLocal(models.Model):
    """
    This class is used to store images that are accessed frequently
    like site background and stored on the site to reduce loading time
    """
    local_image_id = models.AutoField(primary_key=True)
    image_owner = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    location = models.ImageField(upload_to='images/local/')

    def __str__(self):
        return f"Uploaded by {self.image_owner.username}"


class Image(models.Model):
    """
    in future maybe add favourite=T/F and public=T/F
    """
    image_id = models.AutoField(primary_key=True)
    local_image = models.ForeignKey(ImageLocal, null=True, blank=True, on_delete=models.CASCADE)
    remote_image = models.ForeignKey(ImageRemote, null=True, blank=True, on_delete=models.CASCADE)
    description = models.CharField(max_length=45, null=True, blank=True)
    upload_date = models.DateTimeField(editable=False, default=django.utils.timezone.now())

    def __str__(self):
        output = f"- Image Id:{self.image_id}" \
                 f"{self.description}" \
                 f"{str(self.local_image)}"\
                 f"{str(self.remote_image)}"\
                 f"Upload date - {str(self.upload_date)}"
        return output

    def save(self, *args, **kwargs):
        if (self.local_image is None and self.remote_image is not None)\
                or (self.local_image is not None and self.remote_image is None):
            if not self.id:
                # if the image doesn't have an id it has only just been created
                self.upload_date = django.utils.timezone.now()
            super().save(*args, **kwargs)
        else:
            raise exceptions.ValidationError("An Image must either have a local_image or a remote_image, but not both")


class ArticleImage(models.Model):
    article_image_id = models.AutoField(primary_key=True)
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
    )
    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['article', 'image'], name="article_image_unique", )
        ]

    def __str__(self):
        output = f" - Image {str(self.article)}" \
                 f" - Used in article {str(self.article)}"
        return output
