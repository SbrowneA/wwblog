from django.test import TestCase
from unittest import skip
from django.test import TransactionTestCase
from django.test import SimpleTestCase
# from django.test import client
from django.core import exceptions

from wwapp.models import *
import time


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
        a_name = "testCreateAuthor"
        a = User.objects.create(username=a_name)
        a.save()
        a2 = User.objects.get(username=a_name)
        self.assertEqual(a, a2)

    # Just checking only the setupTestData users are save to to the DB
    def test_num_users(self):
        num_authors = User.objects.all().count()
        self.assertEqual(len(self.authors), num_authors)

    def test_print_user(self):
        u = User.objects.get(username=self.authors[0].username)
        user_str = str(u)
        self.assertIn(str(u.username), user_str)
        self.assertIn(str(u.user_id), user_str)


@skip("Skipped  CategoryModelTests")
class CategoryModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # users
        # super().setUpTestData()
        author_names = ['testAuthor1', 'testAuthor2', 'testAuthor3', 'testAuthor4']
        cls.authors = []
        for u in author_names:
            user = User(username=u)
            user.save()
            cls.authors.append(user)

        # create project
        cat_name = f"main_test_proj-{int(time.time() * 10000)}"
        cls.prj = Category(category_creator=cls.authors[0], category_name=cat_name)
        cls.prj.save()

    # def test_create_and_save_project(self):
    #     cat_name = f"main_test_proj-{int(time.time() * 1000)}"
    #     self.cat_names=
    #     self.cat = Category(category_creator=self.authors[0], category_name=cat_name)
    #     self.cat.save()
    #     self.asserrt

    # def test_category_item_created_when_topic_saved(self):
    #     cat_name = f"test_topic-{int(time.time() * 10000)}"
    #     topic = Category(category_creator=self.authors[0], category_type=Category.CategoryType.TOPIC, category_name=cat_name)
    #     topic.save()
        # self.prj.

    def test_create_and_save_topic(self):
        # with self.assertRaises(exceptions.ObjectDoesNotExist):
        #     cat_name = f"main_test_proj-{int(time.time() * 1000)}"
        #     Category.objects.get(category_name=cat_name)
        # cat.add_child_item()
        pass

    def test_assign_topic_to_project(self):
        pass

    # def tearDownClass(cls):
    #     pass
        # delete all the test objects created


"""

@skip("Skipped  ArticleModelTests")
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


    # @classmethod
    # def tearDownClass(cls):
        # cls.article1

"""


