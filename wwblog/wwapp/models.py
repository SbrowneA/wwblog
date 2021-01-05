from django.core import exceptions as djangoex
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
    # test = models.CharField(max_length=20)
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(unique=True, max_length=45)
    # category_parent = models.ForeignKey("Category", on_delete=models.CASCADE, null=True, blank=True)
    category_creator = models.ForeignKey(User, on_delete=models.CASCADE)
    category_type = models.CharField(max_length=45, default="ROOT")

    class Meta:
        indexes = [
            models.Index(fields=['category_name']),
        ]

    # def get_child_categories(self):
    #     return Category.objects.filter(category_parent=self.category_id)

    def get_parent_category(self):
        try:
            i = CategoryItem.objects.filter(category_id=self.category_id)
            a = CategoryItemAssignation.objects.filter(item_id=i.item_id)
            return Category.objects.get(category_id=a.parent_category)
        except djangoex.ObjectDoesNotExist:
            return -1

    def get_parent_category_name(self):
        try:
            return self.get_parent_category().category_name
        except djangoex.ObjectDoesNotExist:
            return ""

    def get_item_assignations(self):
        return CategoryItemAssignation.objects.filter(parent_category_id=self.category_id)

    def get_items(self):
        assignations = self.get_item_assignations()
        items = []
        for a in assignations:
            item = CategoryItem.objects.get(item_id=a.item_id)
            items.append(item)
        return items

    @staticmethod
    def get_root_categories():
        return Category.objects.filter(category_type="PROJECT")

    def __str__(self):
        # parent_cat = self.get_parent_category()
        parent_cat_name = self.get_parent_category_name()
        # if parent_cat != -1:
        #     parent_cat_name = parent_cat.category_name
        # else:
        #     parent_cat_name = ""

        output = f"Category:{self.category_name} " \
                 f"\n- Parent{parent_cat_name} " \
                 f"\n- By: {self.category_creator.username}"
        return output


class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    article_title = models.CharField(max_length=45, default=None, blank=True)
    pub_date = models.DateTimeField(default=None)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=None, blank=True, null=True)
    visits = models.IntegerField(default=0)
    published = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
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

    def get_article_editors(self):
        editors = -1
        try:
            editors = ArticleEditor.objects.filter(article_id=self.article_id)
            if len(editors) == 0:
                editors = -1
            return editors
        except djangoex.ObjectDoesNotExist:
            return editors

    @staticmethod
    def get_latest_articles(count):
        latest_articles = Article.objects.order_by('-pub_date')[:int(count)]
        return latest_articles

    def __str__(self):
        output = f"\n - ID: {self.article_id}" \
                 f"\n - Title: {self.article_title}" \
                 f"\n - By: {self.author.username}"
        # f"\n - Creation Date: {self.pub_date}"
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
        category = Article.objects.get(article_id=self.category_id)
        editor = User.objects.get(user_id=self.editor_id)

        output = f"Article\n{category.__str__()}" \
                 f"Editor\n{editor.__str__()}"
        return output


class CategoryItem(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_article_id = models.OneToOneField(Article, on_delete=models.CASCADE, null=True, blank=True)
    item_category_id = models.OneToOneField(Category, on_delete=models.CASCADE, null=True, blank=True)


class CategoryItemAssignation(models.Model):
    item_assignation_id = models.AutoField(primary_key=True)
    # parent_category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, blank=False)
    parent_category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, blank=False)
    # item = models.ForeignKey(CategoryItem, on_delete=models.CASCADE, null=False, blank=False)
    item = models.OneToOneField(CategoryItem, on_delete=models.CASCADE, null=False, blank=False, unique=True)
    position = models.IntegerField(null=False, blank=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['item', 'position'], name="category_item_unique", )
        ]

# STATIC METHODS
