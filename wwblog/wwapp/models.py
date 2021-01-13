from django.core import exceptions
from django.shortcuts import get_object_or_404
# from django.core import exceptions as djangoex
# from django.utils import timezone
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
        SUBTOPIC = 'SUBTOPIC', _('Sub-Topic')

    category_type = models.CharField(max_length=45, choices=CategoryType.choices, default=CategoryType.PROJECT)

    class Meta:
        indexes = [
            models.Index(fields=['category_name']),
        ]

    def is_project(self):
        return self.category_type == self.CategoryType.PROJECT

    def get_parent_category(self):
        try:
            i = CategoryItem.objects.get(item_category_id=self.category_id)
            a = CategoryItemAssignation.objects.get(item_id=i.item_id)
            return Category.objects.get(category_id=a.parent_category_id)
        except exceptions.ObjectDoesNotExist:
            raise exceptions.ObjectDoesNotExist

    def get_parent_category_name(self):
        try:
            return self.get_parent_category().category_name
        except exceptions.ObjectDoesNotExist:
            return ""

    # get the child categories and articles
    def get_item_assignations(self):
        try:
            return CategoryItemAssignation.objects.filter(parent_category_id=self.category_id)
        except exceptions.EmptyResultSet:
            raise exceptions.EmptyResultSet

    def get_items(self):
        try:
            assignations = self.get_item_assignations()
            items = []
            for a in assignations:
                item = CategoryItem.objects.get(item_id=a.item_id)
                items.append(item)
            return items
        except exceptions.ObjectDoesNotExist:
            return []

    def get_child_categories(self):
        items = self.get_items()
        sub_cats = []
        for i in items:
            if i.item_category_id is not None:
                sub_cat = Category.objects.get(category_id=i.item_category_id)
                sub_cats.append(sub_cat)
        return sub_cats

    def get_child_articles(self):
        items = self.get_items()
        articles = []
        for i in items:
            if i.item_article_id is not None:
                a = Article.objects.get(article_id=i.item_article_id)
                articles.append(a)
        return articles

    def get_category_editors(self):
        try:
            # TODO make sure working correctly
            editors = CategoryEditor.objects.filter(category_id=self.category_id)
            if len(editors) != 0:
                return editors
            return []
        except exceptions.ObjectDoesNotExist:
            return []

    @staticmethod
    def get_root_categories():
        return Category.objects.filter(category_type=Category.CategoryType.PROJECT)

    # def reorder_assignations(self):
        # pass

    def get_child_assignations(self):
        try:
            a_list = CategoryItemAssignation.objects.filter(parent_category_id=self.category_id)
        except exceptions.EmptyResultSet:
            a_list = []
        return a_list

    # def add_child_article(self):
    # TODO needed if PROJECT cant contain articles
    def add_child_category(self, child_cat):
        child_cat.save()  # save child_cat to make its category item
        if self.category_type is not self.CategoryType.SUBTOPIC:
            if self.category_type is self.CategoryType.PROJECT:
                child_cat.CategoryType = self.CategoryType.TOPIC
            elif self.category_type is self.CategoryType.TOPIC:
                child_cat.CategoryType = self.CategoryType.SUBTOPIC

            i = CategoryItem.objects.get(item_category_id=child_cat.category_id)
            # print(f"{len(i_list)} Items retrieved:\n")
            # for i in i_list:
            #     print(f"- ID:{i.item_id} - Category ID: {i.item_category_id}\n")
            #     print(f"{i.__str__()}\n")

            child_cat.save()
            self.add_child_item(i)

        else:
            raise ValueError("This Category is invalid")

    def add_child_item(self, child_item):
        last_pos = len(self.get_child_assignations())
        try:
            # get item assignation and assign parent to self
            a = CategoryItemAssignation.objects.get(item_id=child_item.item_id)
            if a.parent_category_id == self.category_id:
                print("This item has already been assigned to the parent category, try moving it instead")
            else:
                a.parent_category_id = self.category_id
                a.position = last_pos
                a.save()
        except exceptions.ObjectDoesNotExist:
            # make new assignation with parent as self
            a = CategoryItemAssignation(parent_category_id=self.category_id, item=child_item, position=last_pos)
            a.save()

    def __set_assignation_position(self, old_pos, new_pos):
        a = CategoryItemAssignation.objects.get(parent_category_id=self.category_id, position=old_pos)
        a.position = new_pos
        a.save()

    def move_child_item(self, child_item, new_pos):
        try:
            if new_pos >= 0:
                raise ValueError("Position new must be greater than 0")
            assignations = self.get_child_assignations().order_by('position')
            moving_a = CategoryItemAssignation.objects.get(item=child_item)
            old_pos = moving_a.position
            new_pos -= 1
            # assign temp position for CategoryItemAssignation being moved
            moving_a.position = assignations.count()
            moving_a.save()
            if new_pos > old_pos:
                for i in range(old_pos, new_pos+1):
                    self.__set_assignation_position(i, i - 1)
                    # a = CategoryItemAssignation.objects.get(parent_category_id=self.category_id, position=i)
                    # a.position = int(a.position-1)
                    # a.save()
            elif new_pos < old_pos:
                for i in range(old_pos, new_pos-1, -1):
                    self.__set_assignation_position(i, i + 1)
            else:
                print("Item was not moved")

            moving_a.position = new_pos
            moving_a()
        except exceptions.ObjectDoesNotExist:
            raise exceptions.ObjectDoesNotExist("Category.move_child_item() "
                                                "-> ObjectDoesNotExist: Unexpected Error occurred")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # create new category item and save
        # TODO validate selected parent_category is valid (must be PROJECT or TOPIC )
        if self.category_type is self.CategoryType.TOPIC or self.CategoryType.SUBTOPIC:
            try:
                CategoryItem.objects.get(item_category=self)
                print(f"No new item was saved the item already exists:\n"
                      f" - id: {self.category_id}")
            except exceptions.ObjectDoesNotExist:
                i = CategoryItem(item_category=self)
                i.save()
                print(f"Category.save()/new CategoryItem created and saved{i.__str__()}")

    def __str__(self):
        parent_cat_name = self.get_parent_category_name()
        if parent_cat_name == "":
            parent_cat_name = "Null"

        output = f" - Category Name:{self.category_name} " \
                 f"\n- Parent: {parent_cat_name} " \
                 f"\n- By: {self.category_creator.username}"
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
    # category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    published = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    # creation_date = models.DateTimeField(default=timezone.now)
    # article_parent = models.ForeignKey("Article", on_delete=models.SET_DEFAULT, default=None, null=True, blank=True)
    # version = models.IntegerField(default=0)

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

    """
    # TODO for versions
    # constraints = [
    #     models.UniqueConstraint(fields=['article_id', 'version'], name='article_id_version_unique')
    # ]
    """

    def save(self, *args, **kwargs):
        # check if CategoryItem already exists
        try:
            CategoryItem.objects.get(item_article_id=self.article_id)
            # if exists no changes need to be made to CategoryItem
            super().save(*args, **kwargs)
        except exceptions.ObjectDoesNotExist:
            # create new category item and save
            i = CategoryItem(item_article=self)
            super().save(*args, **kwargs)
            i.save()

    def get_editors(self):
        try:
            # TODO make sure working correctly
            editors = ArticleEditor.objects.filter(article_id=self.article_id)
            if len(editors) != 0:
                return editors
            return []
        except exceptions.ObjectDoesNotExist:
            return []

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
        category = Category.objects.get(category_id=self.category_id)
        editor = User.objects.get(user_id=self.editor_id)

        output = f"Category\n{category.__str__()}" \
                 f"Editor\n{editor.__str__()}"
        return output


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
        if (self.item_article_id is None and self.item_category_id is not None) or\
                (self.item_category_id is None and self.item_article_id is not None):
            super().save()
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


# def catTest():
#     proj = Category.objects.get(category_name="Root")
#     user = User.objects.get(username="Big Mike")
#     topic = Category(category_name="project's topic", category_creator=user)
#     proj.add_child_category(topic)
