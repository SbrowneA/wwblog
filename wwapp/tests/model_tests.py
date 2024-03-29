from django.test import TestCase
from django.db import IntegrityError
# from django.test import TransactionTestCase
# from django.test import SimpleTestCase
# from django.test import client
from django.core import exceptions
from unittest import skip
from wwapp.models import (Article, ArticleEditor, ArticleVersion,
                          Category, CategoryEditor, CategoryItem,
                          CategoryItemAssignation)
import time
from .setups import setup_members, setup_moderators, setup_superuser, setup_groups, setup_admins
from django.contrib.auth import get_user_model

User = get_user_model()


def get_micro_time():
    return int(time.time() * 1000)


# @skip("Skipped  UserModelTests")
class UserModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.groups = setup_groups()
        cls.members = setup_members()
        cls.moderators = setup_moderators()
        cls.admins = setup_admins()
        cls.superuser = setup_superuser()

    def test_create_user(self):
        print(f"TEST START:{self._testMethodName}")
        a_name = "testCreateAuthor"
        a = User.objects.create_user(username=a_name, email=f"{a_name}@mail.com", password="testword")
        a.save()
        a2 = User.objects.get(username=a_name)
        self.assertEqual(a, a2)

    # Just checking only the setupTestData users are saved to to the DB
    def test_num_users(self):
        print(f"TEST START:{self._testMethodName}")
        num_authors = User.objects.all().count()
        # +1 == superuser
        self.assertEqual((len(self.members) + len(self.moderators) + len(self.admins)) + 1, num_authors)

    def test_user_to_string(self):
        print(f"TEST START:{self._testMethodName}")
        u = User.objects.get(username=self.members[0].username)
        user_str = str(u)
        self.assertIn(str(u.username), user_str)
        self.assertIn(str(u.id), user_str)

    def test_get_roles_user_throws_value_error(self):
        print(f"TEST START:{self._testMethodName}")
        self.assertRaises(ValueError, User.objects.get_role_users, "a role")

    def test_get_roles_user(self):
        print(f"TEST START:{self._testMethodName}")
        a = self.admins[0].groups

        # for role_name in role_hierarchy:
        #     users = User.objects.get_role_users(role_name)
        #     self.assertEqual(len(users), len(self.admins))

        admins = User.objects.get_role_users("admin")
        mods = User.objects.get_role_users("moderator")
        members = User.objects.get_role_users("member")
        self.assertEqual(len(mods), len(self.admins))
        self.assertEqual(len(mods), len(self.moderators))
        self.assertEqual(len(members), len(self.members))

    def test_get_users_up_to_role(self):
        print(f"TEST START:{self._testMethodName}")
        mods_members = User.objects.get_users_up_to_role("admin")
        self.assertEqual(len(mods_members), (len(self.moderators) + len(self.members)))

    def test_activate_user(self):
        print(f"TEST START:{self._testMethodName}")
        u = self.members[0]
        self.assertFalse(u.is_active)
        self.assertTrue(User.objects.activate_user(u))
        self.assertTrue(u.is_active)


# @skip("Skipped  CategoryModelTests")
class CategoryModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # super().setUpTestData()
        print("Setting up test data")
        # create users
        cls.authors = setup_members()
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
        cls.authors = setup_members()

        cls.main_article = Article.objects.create(author=cls.authors[0],
                                                  article_title="main-article")
        # cls.main_article = Article(author=cls.authors[0],
        #                            article_title="main-article")
        # cls.main_article.save()
        # cls.main_handler = ArticleHandler(cls.main_article)

    # model test
    def test_save_article_creates_category_item(self):
        print(f"\nTEST START:{self._testMethodName}")
        a = Article(article_title="title", author=self.authors[1])
        a.save()
        i = CategoryItem.objects.get(item_article_id=a.article_id)
        items = CategoryItem.objects.all()
        self.assertIsInstance(i, CategoryItem)
        self.assertEqual(2, len(items))

    def test_save_article_does_not_create_duplicate_category_item(self):
        print(f"\nTEST START:{self._testMethodName}")
        a = Article.objects.create(author=self.authors[1])
        i = CategoryItem.objects.get(item_article_id=a.article_id)
        print(i)
        items1 = CategoryItem.objects.all()
        a.save()

        items2 = CategoryItem.objects.all()
        self.assertEqual(len(items1), len(items2))
        i2 = CategoryItem.objects.get(item_article_id=a.article_id)
        self.assertEqual(i, i2)
        self.assertIsInstance(i, CategoryItem)
        self.assertIsInstance(i2, CategoryItem)

    def test_save_article_raises_validation_error_if_published_to_no_category(self):
        print(f"\nTEST START:{self._testMethodName}")
        self.main_article.published = True
        self.assertRaises(IntegrityError, self.main_article.save)

    def test_delete_article_deletes_item_and_assignation(self):
        print(f"\nTEST START:{self._testMethodName}")
        a_id = self.main_article.article_id
        item_id = CategoryItem.objects.get(item_article_id=a_id).item_id
        self.main_article.delete()

        self.assertRaises(exceptions.ObjectDoesNotExist, CategoryItem.objects.get, item_article_id=a_id)
        qs = CategoryItem.objects.all()
        self.assertEqual(0, len(qs))
        self.assertRaises(exceptions.ObjectDoesNotExist, CategoryItemAssignation.objects.get, item_id=item_id)
        qs = CategoryItemAssignation.objects.all()
        self.assertEqual(0, len(qs))

    def test_save_creates_article_version(self):
        print(f"\nTEST START:{self._testMethodName}")
        a = Article.objects.create(author=self.authors[0])
        av = ArticleVersion.objects.get(article_id=a.article_id)
        self.assertIsInstance(a, Article)
        self.assertIsInstance(av, ArticleVersion)
