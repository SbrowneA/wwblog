from django.test import TestCase
from django.test import TransactionTestCase
from django.test import SimpleTestCase
# from django.test import client
from django.core import exceptions
from unittest import skip

from wwapp.models import *
from wwapp.handlers import *
import time


def get_micro_time():
    return int(time.time() * 1000)


# @skip("Skipped  UserModelTests")
class UserModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # User.objects
        author_names = ['testAuthor1', 'testAuthor2', 'testAuthor3', 'testAuthor4']
        cls.authors = []
        for name in author_names:
            a = User.objects.create(username=name)
            a.save()
            cls.authors.append(a)

    def test_create_user(self):
        print(f"TEST START:{self._testMethodName}")
        a_name = "testCreateAuthor"
        a = User.objects.create(username=a_name)
        a.save()
        a2 = User.objects.get(username=a_name)
        self.assertEqual(a, a2)

    # Just checking only the setupTestData users are saved to to the DB
    def test_num_users(self):
        print(f"TEST START:{self._testMethodName}")
        num_authors = User.objects.all().count()
        self.assertEqual(len(self.authors), num_authors)

    def test_user_to_string(self):
        print(f"TEST START:{self._testMethodName}")
        u = User.objects.get(username=self.authors[0].username)
        user_str = str(u)
        self.assertIn(str(u.username), user_str)
        self.assertIn(str(u.user_id), user_str)


# @skip("Skipped  CategoryModelTests")
class CategoryModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # super().setUpTestData()
        print("Setting up test data")
        # create users
        author_names = ['testAuthor1', 'testAuthor2', 'testAuthor3', 'testAuthor4']
        cls.authors = []
        for u in author_names:
            user = User(username=u)
            user.save()
            cls.authors.append(user)

        # create project
        cls.prj_name = f"main_test_proj-{int(time.time() * 10000)}"
        cls.prj = Category(category_creator=cls.authors[0], category_name=cls.prj_name)
        cls.prj.save()
        print("Setting up test data complete")

    # make sure CategoryItem is not created when project is saved
    def test_create_and_save_project(self):
        print(f"TEST START:{self._testMethodName}")
        cat_name = f"test_proj-{get_micro_time()}"
        p = Category(category_creator=self.authors[0], category_name=cat_name)
        p.save()
        print(str(p))
        # p.save()
        cat_id = p.category_id
        self.assertRaises(exceptions.ObjectDoesNotExist, CategoryItem.objects.get, item_category_id=cat_id)

    # make sure CategoryItem is only created when the category is a TOPIC or SUBTOPIC
    def test_category_item_created_when_topic_saved(self):
        print(f"TEST START:{self._testMethodName}")
        topic_name = f"test_topic-{get_micro_time()}"
        p = Category(category_creator=self.authors[0], category_name=topic_name, category_type=Category.CategoryType.TOPIC)
        p.save()
        print(str(p))
        # p.save()
        cat_id = p.category_id
        i = CategoryItem.objects.get(item_category_id=cat_id)
        self.assertIsInstance(i, CategoryItem)

    def test_category_item_created_when_subtopic_saved(self):
        print(f"TEST START:{self._testMethodName}")
        topic_name = f"test_topic-{get_micro_time()}"
        p = Category(category_creator=self.authors[0], category_name=topic_name,
                     category_type=Category.CategoryType.SUBTOPIC)
        p.save()
        print(str(p))
        # p.save()
        cat_id = p.category_id
        i = CategoryItem.objects.get(item_category_id=cat_id)
        self.assertIsInstance(i, CategoryItem)

    def test_assign_project_to_project(self):
        print(f"TEST START:{self._testMethodName}")
        topic_name = f"test_topic-{get_micro_time()}"
        child_prj = Category(category_creator=self.authors[0], category_name=topic_name,
                             category_type=Category.CategoryType.PROJECT)
        child_prj.save()
        handler = CategoryHandler(self.prj)
        handler.add_child_category(child_prj)

        i = CategoryItem.objects.get(item_category_id=child_prj.category_id)
        a = CategoryItemAssignation.objects.get(item_id=i.item_id)
        self.assertEqual(child_prj.category_type, Category.CategoryType.TOPIC)
        self.assertEqual(a.parent_category_id, self.prj.category_id)
        self.assertIsInstance(a, CategoryItemAssignation)

    def test_assign_topic_to_project(self):
        print(f"TEST START:{self._testMethodName}")
        topic_name = f"test_subtopic-{get_micro_time()}"
        child_prj = Category(category_creator=self.authors[0], category_name=topic_name,
                             category_type=Category.CategoryType.SUBTOPIC)
        child_prj.save()
        print(child_prj)
        handler = CategoryHandler(self.prj)
        handler.add_child_category(child_prj)

        child_prj = Category.objects.get(category_id=child_prj.category_id)
        i = CategoryItem.objects.get(item_category_id=child_prj.category_id)
        a = CategoryItemAssignation.objects.get(item_id=i.item_id)
        self.assertEqual(child_prj.category_type, Category.CategoryType.TOPIC)
        self.assertEqual(a.parent_category_id, self.prj.category_id)
        self.assertIsInstance(a, CategoryItemAssignation)

    def test_assign_subtopic_to_project(self):
        print(f"TEST START:{self._testMethodName}")
        topic_name = f"test_subtopic-{get_micro_time()}"
        child_prj = Category(category_creator=self.authors[0], category_name=topic_name,
                             category_type=Category.CategoryType.SUBTOPIC)
        child_prj.save()
        print(child_prj)
        handler = CategoryHandler(self.prj)
        handler.add_child_category(child_prj)

        child_prj = Category.objects.get(category_id=child_prj.category_id)
        i = CategoryItem.objects.get(item_category_id=child_prj.category_id)
        a = CategoryItemAssignation.objects.get(item_id=i.item_id)
        self.assertEqual(child_prj.category_type, Category.CategoryType.TOPIC)
        self.assertEqual(a.parent_category_id, self.prj.category_id)
        self.assertIsInstance(a, CategoryItemAssignation)

    @skip("test_delete_child_category - not complete")
    def test_move_child_item(self):
        # make multiple child items and assign them
        handler = CategoryHandler(self.prj)
        num_child = 10
        for i in range(num_child):
            topic_name = f"test_subtopic-{get_micro_time()}"
            child_prj = Category(category_creator=self.authors[0], category_name=topic_name)
            child_prj.save()
            handler.add_child_category(child_prj)

        child_items = handler.get_items()
        move_i = child_items[0]
        move_a = CategoryItemAssignation.objects.get(item_id=move_i.item_id)
        old_pos = move_a.position

    @skip("test_delete_child_category - not complete")
    def test_delete_child_category(self):
        handler = CategoryHandler(self.prj)
        num_child = 10
        for i in range(num_child):
            topic_name = f"test_subtopic-{get_micro_time()}"
            child_prj = Category(category_creator=self.authors[0], category_name=topic_name)
            child_prj.save()
            handler.add_child_category(child_prj)
        # TODO remove a category
        del_cat = handler.get_child_categories()[3]
        handler.delete_child_category(del_cat)
        a = handler.get_child_assignations()
        self.assertEqual(num_child - 1, len(a))

    def test_category_to_string(self):
        print(f"{self._testMethodName}")
        cat_str = self.prj.__str__()
        self.assertIn(self.prj_name, cat_str)
        self.assertIn(self.prj.category_creator.username, cat_str)
        self.assertIn(self.prj.category_type, cat_str)

    # def test_remove_child_category(self):
    #     pass


class ArticleModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.authors = ['testAuthor1', 'testAuthor2', 'testAuthor3', 'testAuthor4']
        for u in cls.authors:
            user = User(username=u)
            u.save()
            cls.authors.append(user)

        # user = User.objects.get(userame="Username0")
        # editors = [
        #     User.objects.get(userame="Username1"),
        #     User.objects.get(userame="Username2"),
        # ]
        # cls.article1 = Article(author=user, article_title="TestArticle1")
        # article2 = Article(author=user, article_title="TestArticle2")
        # article3 = Article(author=user, article_title="TestArticle3")
        # cls.article1.save()
        # article2.save()
        # article3.save()

    def test_add_editor_to_article(self):
        # self.article1.article_id
        pass
