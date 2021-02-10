from django.core import exceptions
from django.db import IntegrityError
from django.test import TestCase
from unittest import skip
from wwapp.models import (Category, CategoryItem,
                          CategoryItemAssignation, ArticleEditor,
                          Article)
from wwapp.handlers import (ArticleHandler, CategoryHandler, _CategoryItemHandler)
from django.contrib.auth import get_user_model
from .setups import setup_authors, setup_superuser, get_micro_time

User = get_user_model()


class CategoryHandlerTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        print(f"\n{cls.__name__}Setting up test data")
        # create users
        cls.authors = setup_authors()
        # create project
        cls.prj_name = f"main_test_proj-{get_micro_time()}"
        cls.prj = Category(category_creator=cls.authors[0], category_name=cls.prj_name)
        cls.prj.save()
        print(f"\n{cls.__name__}Setting up test data complete")

    # make sure CategoryItem is not created when project is saved
    def test_create_and_save_project(self):
        print(f"\nTEST START:{self._testMethodName}")
        cat_name = f"test_proj-{get_micro_time()}"
        p = Category.objects.create(category_creator=self.authors[0], category_name=cat_name)
        # p = Category(category_creator=self.authors[0], category_name=cat_name)
        # p.save()
        cat_id = p.category_id
        self.assertRaises(exceptions.ObjectDoesNotExist, CategoryItem.objects.get, item_category_id=cat_id)

    # make sure CategoryItem is only created when the category is a TOPIC or SUBTOPIC
    def test_category_item_created_when_topic_saved(self):
        print(f"\nTEST START:{self._testMethodName}")
        topic_name = f"test_topic-{get_micro_time()}"
        p = Category.objects.create(category_creator=self.authors[0], category_name=topic_name,
                                    category_type=Category.CategoryType.TOPIC)
        # print(str(p))
        cat_id = p.category_id
        i = CategoryItem.objects.get(item_category_id=cat_id)
        self.assertIsInstance(i, CategoryItem)

    def test_category_item_created_when_subtopic_saved(self):
        print(f"\nTEST START:{self._testMethodName}")
        topic_name = f"test_topic-{get_micro_time()}"
        p = Category.objects.create(category_creator=self.authors[0], category_name=topic_name,
                                    category_type=Category.CategoryType.SUBTOPIC)
        # print(str(p))
        cat_id = p.category_id
        i = CategoryItem.objects.get(item_category_id=cat_id)
        self.assertIsInstance(i, CategoryItem)

    def test_assign_project_to_project(self):
        print(f"\nTEST START:{self._testMethodName}")
        topic_name = f"test_topic-{get_micro_time()}"
        child_prj = Category.objects.create(category_creator=self.authors[0], category_name=topic_name,
                                            category_type=Category.CategoryType.PROJECT)
        handler = CategoryHandler(self.prj)
        handler.add_child_category(child_prj)

        i = CategoryItem.objects.get(item_category_id=child_prj.category_id)
        a = CategoryItemAssignation.objects.get(item_id=i.item_id)
        self.assertEqual(child_prj.category_type, Category.CategoryType.TOPIC)
        self.assertEqual(a.parent_category_id, self.prj.category_id)
        self.assertIsInstance(a, CategoryItemAssignation)

    def test_assign_topic_to_project(self):
        print(f"\nTEST START:{self._testMethodName}")
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
        print(f"\nTEST START:{self._testMethodName}")
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
        print(f"\nTEST START:{self._testMethodName}")
        # make multiple child items and assign them
        handler = CategoryHandler(self.prj)
        num_child = 10
        for i in range(num_child):
            topic_name = f"test_subtopic-{get_micro_time()}"
            child_prj = Category.objects.create(category_creator=self.authors[0], category_name=topic_name)
            handler.add_child_category(child_prj)

        child_items = handler.get_child_items()
        move_i = child_items[0]
        move_a = CategoryItemAssignation.objects.get(item_id=move_i.item_id)
        old_pos = move_a.position
        handler.move_child_item(child_item=move_i, new_pos=5)
        self.assertEqual((handler.get_child_items()), 10)
        last = handler.get_child_assignations()[-1]
        # self.assertEqual()

    # @skip("test_delete_child_category - not complete")
    def test_delete_child_category(self):
        print(f"\nTEST START:{self._testMethodName}")
        handler = CategoryHandler(self.prj)
        num_child = 10
        for i in range(num_child):
            topic_name = f"test_subtopic-{get_micro_time()}"
            print(topic_name)
            child_prj = Category.objects.create(category_creator=self.authors[0], category_name=topic_name)
            handler.add_child_category(child_prj)
        del_cat = handler.get_child_categories()[3]
        CategoryHandler.delete_category(del_cat)

        assignations = handler.get_child_assignations()
        self.assertEqual(num_child - 1, len(assignations))
        # check all positions were adjusted correctly
        for i in range(0, len(assignations)):
            self.assertEqual(i, assignations[i].position)


class ArticleHandlerTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        print(f"\n{cls.__name__}: Setup Test Data")
        # super().setUpTestData()
        cls.authors = setup_authors()

        cls.main_article = Article.objects.create(author=cls.authors[0],
                                                  article_title="main-article")
        cls.main_handler = ArticleHandler(cls.main_article)
        print(f"\n{cls.__name__}: Setup Test Data Complete")

    def test_get_editor(self):
        print(f"\n{self._testMethodName}")
        self.main_handler.add_editor(self.authors[1])
        e = self.main_handler.get_editor(self.authors[1])
        self.assertIsInstance(e, ArticleEditor)

    def test_get_editor_returns_none_when_object_does_not_exits(self):
        print(f"\n{self._testMethodName}")
        self.assertIsNone(self.main_handler.get_editor(self.authors[1]))
        # self.assertRaises(exceptions.ObjectDoesNotExist, self.main_handler.get_editor, self.authors[1])

    def test_get_editors(self):
        print(f"\n{self._testMethodName}")
        self.main_handler.add_editor(self.authors[1])
        self.main_handler.add_editor(self.authors[2])
        editors = self.main_handler.get_editors()
        self.assertEqual(2, len(editors))
        for e in editors:
            self.assertIsInstance(e, ArticleEditor)

    def test_get_editors_returns_none_when_empty(self):
        print(f"\n{self._testMethodName}")
        a = Article.objects.create(author=self.authors[2], article_title="unrelated article")

        self.assertIsNone(self.main_handler.get_editors())
        ArticleHandler(a).add_editor(self.authors[3])

    def test_get_latest_articles(self):
        print(f"\n{self._testMethodName}")
        # make 5 articles
        articles = []
        for i in range(5):
            a = Article(article_title="article-i", author=self.authors[0])
            articles.append(a)
            a.save()
        # get only 3 latest
        latest = ArticleHandler.get_latest_published_articles(3)
        for i in range(0, 3, -1):
            self.assertEqual(articles[i + 2], latest[i])

    def test_get_no_editors_returns_none(self):
        print(f"\n{self._testMethodName}")
        self.assertIsNone(self.main_handler.get_editors())

    def test_add_editor_to_article(self):
        print(f"\n{self._testMethodName}")
        self.main_handler.add_editor(self.authors[1])
        editors = self.main_handler.get_editors()
        self.assertEqual(1, len(editors))

    def test_add_creator_as_editor_to_article(self):
        print(f"\n{self._testMethodName}")
        c = self.main_article.author
        self.assertRaises(exceptions.ValidationError, self.main_handler.add_editor, c)

    def test_duplicate_editor_is_not_created(self):
        print(f"\n{self._testMethodName}")
        c = self.authors[1]
        self.main_handler.add_editor(c)
        self.assertRaises(IntegrityError, self.main_handler.add_editor, c)

    def test_remove_editor(self):
        print(f"\n{self._testMethodName}")
        self.main_handler.add_editor(self.authors[1])
        self.main_handler.add_editor(self.authors[2])
        self.main_handler.remove_editor(self.authors[1])
        self.assertEqual(1, len(self.main_handler.get_editors()))

    def test_remove_editor_cannot_remove_creator(self):
        print(f"\n{self._testMethodName}")
        # self.assertRaises(exceptions.ValidationError, self.main_handler.remove_editor, self.authors[0])
        self.assertRaises(exceptions.ValidationError, self.main_handler.remove_editor, self.authors[0])

    def test_remove_editor_raises_object_does_not_exist(self):
        print(f"\n{self._testMethodName}")
        user = User(username="username", email="email", password="password", )
        self.assertRaises(exceptions.ObjectDoesNotExist, self.main_handler.remove_editor, user)

    def test_publish_article(self):
        print(f"\n{self._testMethodName}")
        # TODO
        pass

    def test_draft_article(self):
        print(f"\n{self._testMethodName}")
        pass

    def test_get_parent_article(self):
        print(f"\n{self._testMethodName}")
        pass
