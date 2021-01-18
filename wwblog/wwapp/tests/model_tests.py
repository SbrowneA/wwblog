from django.test import TestCase
from django.db import models, IntegrityError
from django.test import TransactionTestCase
from django.test import SimpleTestCase
# from django.test import client
from django.core import exceptions
from unittest import skip

from wwapp.models import *
from wwapp.handlers import *
import time


# to make dummy users
def setup_authors():
    authors = []
    author_names = ['testAuthor1', 'testAuthor2', 'testAuthor3', 'testAuthor4']
    for u in author_names:
        user = User(username=u)
        user.save()
        authors.append(user)
    return authors


def get_micro_time():
    return int(time.time() * 1000)


# @skip("Skipped  UserModelTests")
class UserModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # User.objects
        cls.authors = setup_authors()

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
        cls.authors = setup_authors()
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
        p = Category(category_creator=self.authors[0], category_name=topic_name,
                     category_type=Category.CategoryType.TOPIC)
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

    def test_delete_category_deletes_category_item(self):
        print(f"\nTEST START:{self._testMethodName}")

    def test_delete_category_deletes_child_items(self):
        print(f"\nTEST START:{self._testMethodName}")

    def delete_category_a(self):
        print(f"\nTEST START:{self._testMethodName}")

    def test_category_to_string(self):
        print(f"\nTEST START:{self._testMethodName}")
        cat_str = self.prj.__str__()
        self.assertIn(self.prj_name, cat_str)
        self.assertIn(self.prj.category_creator.username, cat_str)
        self.assertIn(self.prj.category_type, cat_str)

    # def test_remove_child_category(self):
    #     pass


class ArticleModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.authors = setup_authors()

        cls.main_article = Article(author=cls.authors[0],
                                   article_title="main-article")
        cls.main_article.save()
        cls.main_handler = ArticleHandler(cls.main_article)

    # model test
    def test_save_article_creates_category_item(self):
        a = Article(article_title="title", author=self.authors[1])
        a.save()
        i = CategoryItem.objects.get(item_article_id=a.article_id)
        items = CategoryItem.objects.all()
        self.assertIsInstance(i, CategoryItem)
        self.assertEqual(2, len(items))

    def test_save_article_does_not_create_duplicate_category_item(self):
        i = CategoryItem.objects.get(item_article_id=self.main_article.article_id)
        items = CategoryItem.objects.all()
        self.assertIsInstance(i, CategoryItem)
        self.assertEqual(1, len(items))
        self.main_article.save()

        i2 = CategoryItem.objects.get(item_article_id=self.main_article.article_id)
        items = CategoryItem.objects.all()
        self.assertEqual(i, i2)
        self.assertIsInstance(i, CategoryItem)
        self.assertIsInstance(i2, CategoryItem)
        self.assertEqual(1, len(items))

    def test_save_article_raises_validation_error_if_published_to_no_category(self):
        self.main_article.published = True
        self.assertRaises(exceptions.ValidationError, self.main_article.save)

    def test_delete_article_deletes_item(self):
        id = self.main_article.article_id
        self.main_article.delete()
        self.assertRaises(exceptions.ObjectDoesNotExist, CategoryItem.objects.get, item_article_id=id)

    def test_delete_article_deletes_assignation(self):
        # todo
        pass
