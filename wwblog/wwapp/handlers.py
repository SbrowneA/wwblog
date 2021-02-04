import os

from django.db import models, IntegrityError
from django.core import exceptions
from .models import (Article, ArticleEditor, ArticleVersion,
                     Category, CategoryEditor, CategoryItem,
                     CategoryItemAssignation)
from wwblog.settings import POSTS_ROOT
from django.contrib.auth import get_user_model

User = get_user_model()


class _CategoryItemHandler:
    def __init__(self, item: CategoryItem):
        self.item = item

    def get_assignation(self) -> CategoryItemAssignation:
        try:
            return CategoryItemAssignation.objects.get(item_id=self.item.item_id)
        except exceptions.ObjectDoesNotExist:
            raise exceptions.ObjectDoesNotExist

    def get_parent_category(self) -> Category:
        try:
            a = self.get_assignation()
            return Category.objects.get(parent_category_id=a.parent_category_id)
        except exceptions.ObjectDoesNotExist:
            raise exceptions.ObjectDoesNotExist(
                f"{self.__class__.__name__} => This CategoryItem has no parent assigned")


class CategoryHandler:
    def __init__(self, parent):
        self.category = parent

    def get_parent_category(self):
        try:
            i = CategoryItem.objects.get(item_category_id=self.category.category_id)
            return _CategoryItemHandler(i).get_parent_category()
        except exceptions.ObjectDoesNotExist:
            raise exceptions.ObjectDoesNotExist

    def get_parent_category_name(self):
        try:
            return self.get_parent_category().category_name
        except exceptions.ObjectDoesNotExist:
            return None

    def get_child_assignations(self) -> [CategoryItemAssignation]:
        try:
            """gets all the child assignations ordered by position"""
            # todo test if > 0 check is required
            li = CategoryItemAssignation.objects.filter(
                parent_category_id=self.category.category_id).order_by('position')
            if li > 0:
                return li
            raise exceptions.EmptyResultSet()
        except exceptions.EmptyResultSet:
            raise exceptions.EmptyResultSet()

    def get_items(self) -> [CategoryItem]:
        try:
            assignations = self.get_child_assignations()
            items = []
            for a in assignations:
                item = CategoryItem.objects.get(item_id=a.item_id)
                items.append(item)
            return items
        except (exceptions.ObjectDoesNotExist, exceptions.EmptyResultSet):
            return None

    def get_child_categories(self) -> [Category]:
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
            editors = CategoryEditor.objects.filter(category_id=self.category.category_id)
            if len(editors) != 0:
                return editors
        except exceptions.EmptyResultSet:
            pass  # pass to return none if the object does not exist (D.R.Y)
        return None

    def add_child_item(self, new_child_item):
        try:
            last_pos = len(self.get_child_assignations())
        except exceptions.EmptyResultSet:
            last_pos = 0

        try:
            # get item assignation and assign parent to self
            a = CategoryItemAssignation.objects.get(item_id=new_child_item.item_id)
            if a.parent_category_id == self.category.category_id:
                raise ValueError("This item has already been assigned to the parent category, try moving it instead")
            else:
                _CategoryItemHandler(new_child_item).get_parent_category()
                a.parent_category_id = self.category.category_id
                a.position = last_pos
                a.save()

        except exceptions.ObjectDoesNotExist:
            # make new assignation with parent as self
            a = CategoryItemAssignation(parent_category_id=self.category.category_id, item=new_child_item,
                                        position=last_pos)
            a.save()

    # def add_child_article(self):
    # TODO needed if PROJECT cant contain articles

    def add_child_category(self, child_cat: Category):
        if self.category.category_type is not Category.CategoryType.SUBTOPIC:
            if self.category.category_type is Category.CategoryType.PROJECT:
                child_cat.category_type = Category.CategoryType.TOPIC
                child_cat.save()
            elif self.category.category_type is Category.CategoryType.TOPIC:
                child_cat.category_type = Category.CategoryType.SUBTOPIC
                child_cat.save()
            child_cat.save()  # save child_cat to make its category item
            i = CategoryItem.objects.get(item_category_id=child_cat.category_id)

            child_cat.save()
            self.add_child_item(i)
        else:
            raise ValueError("This Category is invalid")

    # used by self.move_child_item
    def __set_assignation_position(self, old_pos: int, new_pos: int):
        a = CategoryItemAssignation.objects.get(parent_category_id=self.category.category_id, position=old_pos)
        a.position = new_pos
        a.save()

    def move_child_item(self, child_item: CategoryItem, new_pos: int):
        # try:
        if new_pos <= 0:
            raise ValueError("Position new must be greater than 0")
        assignations = self.get_child_assignations()
        moving_a = _CategoryItemHandler(child_item).get_assignation()
        old_pos = moving_a.position
        new_pos -= 1
        # assign temp position for CategoryItemAssignation being moved
        moving_a.position = len(assignations)
        moving_a.save()
        if new_pos > old_pos:
            for i in range(old_pos, new_pos + 1):
                self.__set_assignation_position(i, i - 1)
        elif new_pos < old_pos:
            for i in range(old_pos, new_pos - 1, -1):
                self.__set_assignation_position(i, i + 1)
        else:
            print("Item was not moved")
        moving_a.position = new_pos
        moving_a.save()
        # except exceptions.ObjectDoesNotExist:
        #     raise exceptions.ObjectDoesNotExist("Category.move_child_item() "
        #                                         "-> ObjectDoesNotExist: Unexpected Error occurred")

    def delete_child_item_assignation(self, child_item: CategoryItem):
        pos = _CategoryItemHandler(child_item).get_assignation().position
        assignations = self.get_child_assignations()
        del_a = _CategoryItemHandler(child_item).get_assignation()
        del_a.delete()
        for i in range(pos + 1, len(assignations)):
            a = assignations[i]
            a.position = a.position - 1
            a.save()

    def delete_child_category(self, del_cat: Category):
        # check sub items
        del_handler = CategoryHandler(del_cat)
        child_items = del_handler.get_items()
        if child_items is not None:
            # delete child items of del_cat
            del_handler.draft_child_articles()
            del_handler.delete_child_categories()
        # un-assign del_cat from self and delete
        self.delete_child_item_assignation(del_handler.get_category_item())
        del_cat.delete()
        # Category.objects.get(category_id=del_cat.category_id)

    def delete_child_categories(self):
        categories = self.get_child_categories()
        for cat in categories:
            self.delete_child_category(cat)

    def draft_child_articles(self):
        articles = self.get_child_articles()
        for a in articles:
            a_handler = ArticleHandler(a)
            # draft_article uses CategoryHandler.delete_child_item_assignation
            a_handler.draft_article()

    def get_category_item(self) -> CategoryItem:
        return CategoryItem.objects.get(item_category_id=self.category.category_id)

    def transfer_child_items(self, new_category):
        # TODO
        # new_category
        # loop through all articles in old cat
        # and assign it to the new category
        pass


class ArticleHandler:
    def __init__(self, article):
        self.article = article

    def get_category_item(self) -> CategoryItem:
        return CategoryItem.objects.get(item_article_id=self.article.article_id)

    def get_parent_category(self) -> Category:
        try:
            return _CategoryItemHandler(self.get_category_item()).get_parent_category()
        except exceptions.ObjectDoesNotExist:
            raise exceptions.ObjectDoesNotExist("The article has no parent category,"
                                                " check the article is not drafted")

    def has_parent_article(self) -> bool:
        if self.article.article_parent is not None:
            return True
        return False

    def has_child_article(self) -> bool:
        try:
            Article.objects.get(article_parent=self.article.article_id)
            return True
        except exceptions.ObjectDoesNotExist:
            return False

    def remove_child_article(self):
        if self.has_child_article():
            a = self.get_child_article()
            a.article_parent = None
            a.save()

    def remove_parent_article(self):
        if self.has_parent_article():
            self.article.article_parent = None
            self.article.save()

    def draft_article(self):
        self.remove_child_article()
        self.remove_parent_article()
        # TODO
        try:
            cat = self.get_parent_category()
            CategoryHandler(cat).delete_child_item_assignation(self.get_category_item())
            self.article.published = False
            self.article.save()
        except exceptions.ObjectDoesNotExist:
            raise exceptions.ObjectDoesNotExist("This article is already drafted")

    def publish_article(self, category: Category):
        item = self.get_category_item()
        # i_handler = _CategoryItemHandler(item)
        # c_handler = CategoryHandler(category)
        # check if already published
        if self.article.published:
            self.draft_article()
        # publish to new category
        cat_handler = CategoryHandler(category)
        cat_handler.add_child_item(item)
        self.article.published = True
        self.article.save()

    def add_editor(self, user):
        try:
            if user.id == self.article.author_id:
                raise exceptions.ValidationError("This author is already the creator and editor of the article")
            else:
                editor = ArticleEditor(editor_id=user.id, article=self.article)
                editor.save()
        except IntegrityError:
            raise IntegrityError("This author is already and editor on this article")

    def remove_editor(self, user: User):
        """remove an article editor object """
        try:
            if user.id == self.article.author_id:
                raise exceptions.ValidationError("The creator of the article cannot be removed")
            else:
                editor = self.get_editor(user)
                if editor is None:
                    raise exceptions.ObjectDoesNotExist
                editor.delete()
        except exceptions.ObjectDoesNotExist:
            raise exceptions.ObjectDoesNotExist("This author is not an editor on this article or they are the creator")
        except exceptions.ValidationError:
            raise exceptions.ValidationError("The creator of the article cannot be removed")

    def get_editors(self):
        # try:
        editors = ArticleEditor.objects.filter(article_id=self.article.article_id)
        if len(editors) == 0:
            return None
            # raise exceptions.EmptyResultSet("This article has no editors")
        return editors

        # except exceptions.EmptyResultSet:
        # raise exceptions.EmptyResultSet("This article has no editors")
        # raise exceptions.EmptyResultSet()

    def get_parent_article(self):
        try:
            return Article.objects.get(article_id=self.article.article_parent_id)
        except exceptions.ObjectDoesNotExist:
            return None

    def get_child_article(self):
        try:
            return Article.objects.get(article_parent_id=self.article.article_id)
        except exceptions.ObjectDoesNotExist:
            return None

    def get_article_group(self) -> [Article]:
        articles = [self.article]
        a = self.article
        # get children
        valid = True
        while valid is True:
            a = ArticleHandler(a).get_child_article()
            if a is not None:
                articles.append(a)
            else:
                valid = False
        # get parents
        valid = True
        a = self.article
        while valid is True:
            a = ArticleHandler(a).get_parent_article()
            if a is not None:
                articles.insert(0, a)
            else:
                valid = False

        if len(articles) == 1:
            raise exceptions.ObjectDoesNotExist
        return articles

    def get_editor(self, user: User):
        try:
            return ArticleEditor.objects.get(editor_id=user.id, article_id=self.article.article_id)
        except exceptions.ObjectDoesNotExist:
            return None

    @staticmethod
    def get_latest_published_articles(count: int) -> [Article]:
        latest_articles = Article.objects.filter(published=True).order_by('-pub_date')[:int(count)]
        return latest_articles

    @staticmethod
    def create_new_article(user):
        a = Article.objects.create(author=user)
        return ArticleHandler(a)

    @staticmethod
    def get_user_published_articles(user: User):
        try:
            return Article.objects.filter(author_id=user.id, published=True).order_by('-pub_date')
        except exceptions.EmptyResultSet:
            return None

    @staticmethod
    def get_user_drafted_articles(user: User):
        try:
            return Article.objects.filter(author_id=user.id, published=False).order_by('-creation_date')
        except exceptions.EmptyResultSet:
            return None

    def get_all_versions(self) -> [ArticleVersion]:
        return ArticleVersion.objects.filter(article_id=self.article.article_id).order_by('version')

    def get_latest_version(self) -> ArticleVersion:
        # creating versions variable because "Negative indexing is not supported."
        # i.e. self.get_all_versions()[-1]
        versions = self.get_all_versions()
        ver = versions[len(versions) - 1]
        return ver

    def __get_latest_file_dir(self) -> str:
        file_name = f"{self.article.article_id}-{self.get_latest_version().version}.html"
        return os.path.join(POSTS_ROOT, file_name)

    # must return T or F!!
    def save_article_content(self, new_content) -> bool:
        file_dir = self.__get_latest_file_dir()
        with open(file_dir, 'w') as file:
            file.write(new_content)
        return True

    def get_article_content(self) -> str:
        file_dir = self.__get_latest_file_dir()
        try:
            with open(file_dir, "r") as file:
                content = file.read()
                print("article content loaded")
            return str(content)
        except FileNotFoundError:
            print("FileNotFoundError was thrown: article content NOT found")
            return ""

    def __remove_latest_file(self):
        file_dir = self.__get_latest_file_dir()
        if os.path.exists(file_dir):
            os.remove(file_dir)
        else:
            # TODO make sure this is not a security risk
            # raise FileNotFoundError(f"file could not be found at {file_dir}")
            raise FileNotFoundError("File for the latest version of this article could not be found")

    def __remove_all_article_files(self):
        all_ver = self.get_all_versions()
        for ver in all_ver:
            file_name = f"{self.article.article_id}-{ver.version}.html"
            file_dir = os.path.join(POSTS_ROOT, file_name)
            if os.path.exists(file_dir):
                os.remove(file_dir)
            else:
                print("This article version has no corresponding file")
                # raise FileNotFoundError("File for the latest version of this article could not be found")

    def delete_article(self):
        if self.article.published:
            self.draft_article()
        self.__remove_all_article_files()
        self.article.delete()
