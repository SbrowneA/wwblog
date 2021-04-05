import os
import hashlib
import traceback

from django.db import (
    # models, \
    IntegrityError)
from django.core import exceptions

from .context_processors import create_presigned_url
from .models import (Article, ArticleEditor, ArticleVersion,
                     Category, CategoryEditor, CategoryItem,
                     CategoryItemAssignation,
                     # Image, ImageLocal
                     )
from wwblog.settings import POSTS_ROOT, POSTS_LOCATION
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from wwblog.storages import MediaStorage
from django.utils import timezone

from account.role_validator import is_moderator_or_admin
from .decorators import time_task

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
            return Category.objects.get(category_id=a.parent_category_id)
        except exceptions.ObjectDoesNotExist:
            raise exceptions.ObjectDoesNotExist(
                f"{self.__class__.__name__} => This CategoryItem has no parent assigned")


class CategoryGroup:
    def __init__(self, category: Category):
        self.category = category
        self.handler = CategoryHandler(category)
        self.articles = self.handler.get_child_articles()

        # list of child category groups
        self.sub_cat_groups = []
        child_cats = self.handler.get_child_categories()
        if child_cats is not None:
            for cat in child_cats:
                group = CategoryGroup(cat)
                self.sub_cat_groups.append(group)


class CategoryHandler:
    def __init__(self, parent):
        self.category = parent

    def has_editor_privilege(self, user: User) -> bool:
        # TODO use 'or' instead of separate statements, this is just for testing
        if is_moderator_or_admin(user):
            return True
        elif self.get_category_editors():
            if user in self.get_category_editors():
                return True
        elif user.id == self.category.category_creator_id:
            return True
        return False

    def get_parent_category(self):
        try:
            i = CategoryItem.objects.get(item_category_id=self.category.category_id)
            return _CategoryItemHandler(i).get_parent_category()
        except exceptions.ObjectDoesNotExist:
            raise exceptions.ObjectDoesNotExist("This CategoryItem has no parent category")

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
            if len(li) > 0:
                return li
            raise exceptions.EmptyResultSet()
        except exceptions.EmptyResultSet:
            raise exceptions.EmptyResultSet()

    def get_child_items(self) -> [CategoryItem]:
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
        items = self.get_child_items()
        sub_cats = []
        if items is not None:
            for i in items:
                if i.item_category_id is not None:
                    sub_cat = Category.objects.get(category_id=i.item_category_id)
                    sub_cats.append(sub_cat)
        return sub_cats

    def get_child_articles(self):
        items = self.get_child_items()
        articles = []
        if items:
            for i in items:
                if i.item_article_id is not None:
                    a = Article.objects.get(article_id=i.item_article_id)
                    articles.append(a)
        return articles

    def get_category_editors(self):
        # TODO test
        try:
            editors = CategoryEditor.objects.filter(category_id=self.category.category_id)
            if len(editors) != 0:
                return editors
        except exceptions.EmptyResultSet:
            pass  # pass to return none if the object does not exist (D.R.Y)
        return None

    def _add_child_item(self, new_child_item):
        try:
            last_pos = len(self.get_child_assignations())
        except exceptions.EmptyResultSet:
            last_pos = 0

        try:
            # TODO **BUG TO FIX HERE **
            #  get parent cat handler remove child item and add to self
            a = CategoryItemAssignation.objects.get(item_id=new_child_item.item_id)
            if a.parent_category_id == self.category.category_id:
                raise ValueError("This item has already been assigned to the parent category, try moving it instead")
            else:
                _CategoryItemHandler(new_child_item).get_parent_category()
                a.parent_category_id = self.category.category_id
                a.position = last_pos
                a.save()

        except exceptions.ObjectDoesNotExist:
            pass
            # make new assignation with parent as self
        assignation = CategoryItemAssignation(parent_category_id=self.category.category_id, item=new_child_item,
                                              position=last_pos)
        assignation.save()

    def add_child_article(self, article: Article):
        if self.category.category_type == Category.CategoryType.TOPIC or \
                self.category.category_type == Category.CategoryType.SUBTOPIC:
            i = CategoryItem.objects.get(item_article_id=article.article_id)
            self._add_child_item(i)
        else:
            raise ValueError(
                f"Articles can only be published to {Category.CategoryType.TOPIC} or {Category.CategoryType.SUBTOPIC}")

    def add_child_category(self, child_cat: Category):
        if self.category.category_id != child_cat.category_id:
            if self.category.category_type is not Category.CategoryType.SUBTOPIC:
                if self.category.category_type == Category.CategoryType.PROJECT:
                    child_cat.category_type = Category.CategoryType.TOPIC
                    # child_cat.save()
                elif self.category.category_type == Category.CategoryType.TOPIC:
                    child_cat.category_type = Category.CategoryType.SUBTOPIC
                    # child_cat.save()
                child_cat.save()  # save child_cat to make its category item
                i = CategoryItem.objects.get(item_category_id=child_cat.category_id)
                # child_cat.save()
                self._add_child_item(i)
        else:
            raise ValueError("This Category is invalid: cannot assign self as child category.")

    # used by self.move_child_item
    def __set_assignation_position(self, old_pos: int, new_pos: int):
        """
        private method that sets the position value of a CategoryItemAssignation object.
        used internally by methods to rearrange the order within a category
        :param old_pos:
        :param new_pos:
        :return:
        """
        a = CategoryItemAssignation.objects.get(parent_category_id=self.category.category_id, position=old_pos)
        a.position = new_pos
        a.save()

    def move_child_item(self, child_item: CategoryItem, new_pos: int):
        """
        changes the position of a child item within a category and adjusts all other items accordingly
        :param child_item:
        :param new_pos:
        :return:
        """
        assignations = self.get_child_assignations()
        if new_pos > len(assignations) or new_pos <= 0:
            raise ValueError("Position new must be greater than 0 "
                             "and within the assignation range i.e. len(assignations)")
        moving_a = _CategoryItemHandler(child_item).get_assignation()
        old_pos = moving_a.position
        new_pos -= 1
        # assign temp position for CategoryItemAssignation being moved
        moving_a.position = len(assignations)
        moving_a.save()
        if new_pos > old_pos:
            for i in range(old_pos + 1, new_pos + 1):
                self.__set_assignation_position(i, i - 1)
        elif new_pos < old_pos:
            for i in range(old_pos - 1, new_pos - 1, -1):
                self.__set_assignation_position(i, i + 1)
        else:
            print("Item was not moved")
        moving_a.position = new_pos
        moving_a.save()
        # except exceptions.ObjectDoesNotExist:
        #     raise exceptions.ObjectDoesNotExist("Category.move_child_item() "
        #                                         "-> ObjectDoesNotExist: Unexpected Error occurred")

    def _delete_child_item_assignation(self, child_item: CategoryItem):
        """
        method only used to assign a child of a category item and re-adjust the succeeding assignations'
        position accordingly. This method is only to be used by other methods such as ArticleHandler.draft_article
        or CategoryHandler.delete_category which handle cases such as article groups or categories with children.
        :param child_item:
        :return:
        """
        pos = _CategoryItemHandler(child_item).get_assignation().position
        assignations = self.get_child_assignations()
        del_a = _CategoryItemHandler(child_item).get_assignation()
        del_a.delete()
        for i in range(pos + 1, len(assignations)):
            a = assignations[i]
            a.position = a.position - 1
            a.save()

    @staticmethod
    def delete_category(del_cat: Category):
        del_handler = CategoryHandler(del_cat)
        # check for and delete child items
        child_items = del_handler.get_child_items()
        if child_items is not None and len(child_items) != 0:
            # delete child items of del_cat
            # TODO test
            del_handler.draft_child_articles()
            del_handler.delete_child_categories()

        # if has parent remove assignation
        try:
            parent = del_handler.get_parent_category()
        except exceptions.ObjectDoesNotExist:
            # TODO test (delete a project)
            parent = None
        if parent is not None:
            parent_handler = CategoryHandler(parent)
            parent_handler._delete_child_item_assignation(del_handler.get_category_item())
        del_cat.delete()

    def delete_child_categories(self):
        # TODO test (with delete_category() that has child categories)
        categories = self.get_child_categories()
        for cat in categories:
            CategoryHandler.delete_category(cat)
            # self.delete_child_category(cat)

    def draft_child_articles(self):
        # TODO test (with delete_category() that has child categories)
        articles = self.get_child_articles()
        for a in articles:
            a_handler = ArticleHandler(a)
            # draft_article uses CategoryHandler.delete_child_item_assignation
            a_handler.draft_article()

    def get_category_item(self) -> CategoryItem:
        return CategoryItem.objects.get(item_category_id=self.category.category_id)

    def transfer_child_items(self, destination_category):
        # TODO incomplete method
        self.get_child_assignations()
        destination_category = CategoryHandler(destination_category)
        # destination_category._add_child_item()

        # loop through all assignations and add them to new cat
        # todo: check if they need to be un assigned first?
        pass

    def get_child_category_type(self):
        # TODO test
        if self.category.category_type == Category.CategoryType.PROJECT:
            return Category.CategoryType.TOPIC
        elif self.category.category_type == Category.CategoryType.TOPIC:
            return Category.CategoryType.TOPIC
        elif self.category.category_type == Category.CategoryType.SUBTOPIC:
            return None

    @staticmethod
    def get_user_projects(user: User) -> [Category]:
        try:
            return Category.objects.filter(category_creator_id=user.id,
                                           category_type=Category.CategoryType.PROJECT).order_by('category_name')
        except exceptions.EmptyResultSet:
            return []

    @staticmethod
    def get_user_topics(user: User) -> [Category]:
        try:
            return Category.objects.filter(category_creator_id=user.id,
                                           category_type=Category.CategoryType.TOPIC).order_by('category_name')
        except exceptions.EmptyResultSet:
            return []

    @staticmethod
    def get_user_subtopics(user: User) -> [Category]:
        try:
            return Category.objects.filter(category_creator_id=user.id,
                                           category_type=Category.CategoryType.SUBTOPIC).order_by('category_name')
        except exceptions.EmptyResultSet:
            return []

    @staticmethod
    def get_editor_topics(user: User) -> [Category]:
        # TODO test
        topics = []
        try:
            editors = CategoryEditor.objects.filter(user_id=user.id)
            for e in editors:
                topic = Category.objects.get(category_id=e.category_id)
                if topic.category_type == Category.CategoryType.TOPIC:
                    topics.append(topic)
                return sorted(topics, key=lambda topic: Category.category_name)
        except exceptions.EmptyResultSet:
            pass  # returns empty topics list
        return topics

    @staticmethod
    def get_editor_subtopics(user: User) -> [Category]:
        # TODO test
        topics = []
        try:
            editors = CategoryEditor.objects.filter(user_id=user.id)
            for e in editors:
                subtopic = Category.objects.get(category_id=e.category_id)
                if subtopic.category_type == Category.CategoryType.SUBTOPIC:
                    topics.append(subtopic)
                return sorted(topics, key=lambda topic: Category.category_name)
                # topics.order_by('category_name')
        except exceptions.EmptyResultSet:
            pass  # returns empty topics list
        return topics
        # except exceptions.ObjectDoesNotExist:
        #     log a critical error

    @staticmethod
    def convert_topics_to_choice(topics: [Category]):
        choices = []
        for t in topics:
            choices.append((f"category-{t.category_id}", f"{t.category_name}"))
        return choices

    @staticmethod
    def convert_articles_to_choice(articles: [Article]):
        choices = []
        for a in articles:
            choices.append((f"article-{a.article_id}", f"{a.article_title}"))
        return choices

    @staticmethod
    def get_publish_to_choices_for_user(user: User):
        choices = []
        # if is_moderator_or_admin(user):
        # get all topics and sub topics
        # get all articles
        # pass
        # else:
        topics = CategoryHandler.get_user_topics(user)
        subtopics = CategoryHandler.get_user_subtopics(user)
        # TODO enable articles once parent article issue is fixed
        # articles = ArticleHandler.get_user_published_articles(user)
        # # articles = sorted(articles, key=lambda article: article.article_title)
        # list(articles).sort(key=lambda article: article.article_title)
        # TODO get editor topics and articles (not just authored)
        # not recommended to load the whole query set in to memory (i.e list()) and only load required variables instead
        topics = list(topics) + list(subtopics)
        choices = CategoryHandler.convert_topics_to_choice(topics)
        # choices += CategoryHandler.convert_articles_to_choice(articles)

        return choices

    @staticmethod
    def get_all_projects() -> [Category]:
        try:
            return Category.objects.filter(category_type=Category.CategoryType.PROJECT).order_by('category_name')
        except exceptions.EmptyResultSet:
            return []

    @staticmethod
    def create_project(user: User) -> Category:
        # get the last id of all Category objects
        try:
            cats = Category.objects.all().order_by('category_id')
            # print(cats)
            if len(cats) > 0:
                # negative indexing is not supported again? (i.e. cats[-1])
                last_cat = cats[len(cats) - 1]
                last_num = last_cat.category_id + 1
            else:
                last_num = 0
        except exceptions.EmptyResultSet:
            last_num = 0
        # ensure category_name is unique
        proj_name = f"Project {last_num}"
        try:
            Category.objects.get(category_name=proj_name)
            unique = False
            while not unique:
                proj_name = f"Project {_make_hash(proj_name)}"
                Category.objects.get(category_name=proj_name)
        except exceptions.ObjectDoesNotExist:
            # pass because the title is unique
            pass
        proj = Category(category_creator_id=user.id,
                        category_type=Category.CategoryType.PROJECT,
                        category_name=proj_name)
        proj.save()
        return proj

    def get_category_group(self) -> CategoryGroup:
        return CategoryGroup(self.category)


class ArticleHandler:

    def __init__(self, article):
        self.article = article
        self.__name__ = "ArticleHandler"

    def has_editor_privilege(self, user: User) -> bool:
        if is_moderator_or_admin(user):
            return True
        elif self.get_editors() and user in self.get_editors():
            return True
        elif user.id == self.article.author_id:
            return True
        return False

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
        # TODO test
        try:
            cat = self.get_parent_category()
            CategoryHandler(cat)._delete_child_item_assignation(self.get_category_item())
            self.article.published = False
            self.article.save()
        except exceptions.ObjectDoesNotExist:
            raise exceptions.ObjectDoesNotExist("This article is already drafted")

    def publish_as_child_article(self, p_article: Article):
        if self.article.published:
            self.draft_article()
        # get cat of parent
        p_handler = ArticleHandler(p_article)
        p_cat = p_handler.get_parent_category()
        # publish to cat
        self.publish_article(p_cat)
        # assign parent
        p_cat_handler = CategoryHandler(p_cat)
        p_assignation = _CategoryItemHandler(p_cat_handler.get_category_item()).get_assignation()
        new_item = self.get_category_item()
        p_cat_handler.move_child_item(new_item, p_assignation.position + 1)
        self.article.article_parent_id = p_article.article_id
        self.article.save()

    def publish_article(self, category: Category):
        # check if already published
        if self.article.published:
            self.draft_article()
        # publish to new category
        cat_handler = CategoryHandler(category)
        cat_handler.add_child_article(self.article)
        self.article.published = True
        self.article.pub_date = timezone.now()
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
        # Article.objects.create does not consistently make CategoryItem
        a = Article(author=user)
        a.save()
        return a

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

    def get_latest_version_url(self) -> str:
        # return self.get_latest_version_url_local()
        # need to replace \ with / to prevent NoSuchKey error
        key = os.path.join("media", self.__get_latest_version_dir()).replace("\\", "/")
        return create_presigned_url(key, 300)

    def __get_latest_version_dir(self) -> str:
        file_name = f"{self.article.article_id}-{self.get_latest_version().version}.html"
        return os.path.join(POSTS_LOCATION, str(self.article.author_id), file_name)
        # return f"{POSTS_ROOT}/{self.article.author_id}/{file_name}"
        # return self.__get_latest_version_dir_local()

    @time_task
    def save_article_content(self, new_content) -> bool:
        # if new_content == "":
        #     self.__remove_all_article_files_local()
        #     return True
        # return self.save_article_content_local(new_content)

        # TODO check for success and notify on front end
        file_dir = self.__get_latest_version_dir()
        storage = MediaStorage()
        # try to delete file if new content is empty
        if new_content == "":
            try:
                if storage.exists(file_dir):
                    self.__remove_all_article_files()
            except FileNotFoundError:
                return False
            return True
        try:
            if storage.exists(file_dir):
                print(f"File will be overridden: {file_dir}")
            else:
                print(f"No file exists, new file was created: {file_dir}")
            file = default_storage.open(file_dir, "w")
            file.write(str(new_content))
            file.close()
            file_url = storage.url(file_dir)
            print(f"saved to: {file_url}")
            return True

        except FileNotFoundError:
            print(f"{self.__name__}.{self.save_article_content.__name__} -> FileNotFoundError was thrown:\n"
                  f"{traceback.print_exc()}")
            return False
        except ValueError:
            print(f"{self.__name__}.{self.save_article_content.__name__} -> The 'posts' directory does not exist")
            return False

    @time_task
    def get_article_content(self) -> str:
        # return self.get_article_content_local()
        file_dir = self.__get_latest_version_dir()
        try:
            # file = default_storage.open(file_dir, "r")
            # content = file.read()
            # file.close()
            storage = MediaStorage()
            # with default_storage.open(file_dir, "r") as file:
            print(f"trying to get file {file_dir}")
            if storage.exists(file_dir):
                with storage.open(file_dir, "r") as file:
                    content = file.read()
                    print("article content loaded successfully")
                return str(content)
            else:
                return ""
        except FileNotFoundError:
            print(f"ArticleHandler.{self.get_article_content.__name__}"
                  f" -> FileNotFoundError was thrown: article content NOT found\n"
                  f"{traceback.print_exc()}")
            return ""

    def __remove_all_article_files(self):
        # self.__remove_all_article_files_local()
        all_ver = self.get_all_versions()
        for ver in all_ver:
            file_name = f"{self.article.article_id}-{ver.version}.html"
            # TODO check if people other than the author can make child articles of an article
            file_dir = os.path.join(POSTS_LOCATION, str(self.article.author_id), file_name)
            storage = MediaStorage()
            if storage.exists(file_dir):
                storage.delete(file_dir)
            else:
                print(f"{self.__remove_all_article_files.__name__}This article version "
                      f"(file dir:{file_dir}) has no corresponding file, file was not deleted")
                # raise FileNotFoundError("File for the latest version of this article could not be found")

    @time_task
    def delete_article(self):
        if self.article.published:
            self.draft_article()
        self.__remove_all_article_files()
        self.article.delete()

    # LOCAL VERSIONS


"""
    def get_latest_version_url_local(self):
        file_name = f"{self.article.article_id}-{self.get_latest_version().version}.html"
        # print(f"LOCATED AT: /media/posts/{file_name}")
        return f"/media/posts/{file_name}"
        # return self.__get_latest_version_dir_local().replace("\\", "/")

    # must return T or F!!
    def save_article_content_local(self, new_content) -> bool:
        # TODO check for success and notify on front end
        try:
            file_dir = self.__get_latest_version_dir()
            with open(file_dir, 'w') as file:
                file.write(new_content)
            return True
        except FileNotFoundError:
            print(f"{self.__name__}.{self.save_article_content.__name__} -> FileNotFoundError was thrown")
            return False

    def get_article_content_local(self) -> str:
        file_dir = self.__get_latest_version_dir()
        try:
            with open(file_dir, "r") as file:
                content = file.read()
                # print("article content loaded")
            return str(content)
        except FileNotFoundError:
            print(f"ArticleHandler.{self.get_article_content_local.__name__}"
                  f" -> FileNotFoundError was thrown: article content NOT found")
            return ""

    def __get_latest_version_dir_local(self) -> str:
        file_name = f"{self.article.article_id}-{self.get_latest_version().version}.html"
        return os.path.join(POSTS_ROOT, str(self.article.author_id), file_name)

    def __remove_latest_file_local(self):
        file_dir = self.__get_latest_version_dir()
        if os.path.exists(file_dir):
            os.remove(file_dir)
        else:
            # TODO make sure this is not a security risk (printing dir)
            # raise FileNotFoundError(f"file could not be found at {file_dir}")
            raise FileNotFoundError("File for the latest version of this article could not be found")

    def __remove_all_article_files_local(self):
        all_ver = self.get_all_versions()
        for ver in all_ver:
            file_name = f"{self.article.article_id}-{ver.version}.html"
            file_dir = os.path.join(POSTS_ROOT, str(self.article.author_id), file_name)
            if os.path.exists(file_dir):
                os.remove(file_dir)
            else:
                print(f"{self.__remove_all_article_files_local().__name__}This article version "
                      f"(file dir:{file_dir}) has no corresponding file, file was not deleted")
                # raise FileNotFoundError("File for the latest version of this article could not be found")


"""

"""
class ImageHandler:
    @staticmethod
    def upload_local_image(image, image_name, user):
        if not user.is_authenticated:
            raise ValueError("User must be logged in to upload")

        if image_name is not None:
            # image_name = f"img-{user.id}-" + _make_hash(f"{user.username}{time.time()}")
            local_img = ImageLocal.objects.create(image_owner=user, location=image)
            local_img.save()
            img = Image.objects.create(local_image=local_img, description="testing")
            img.save()

    def get_user_images(self, user):
        images = []
        # Image.objects.filter()
        return images
"""


def _make_hash(value: str) -> str:
    # encoded = value.encode('utf=8')
    h = hashlib.sha224(value.encode('utf=8'), usedforsecurity=False)
    return str(h)
