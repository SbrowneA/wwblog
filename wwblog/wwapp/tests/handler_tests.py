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

    def test_assign_self_to_self_as_topic_raises_value_error(self):
        print(f"\nTEST START:{self._testMethodName}")
        handler = CategoryHandler(self.prj)
        with self.assertRaises(ValueError):
            handler.add_child_category(self.prj)

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

    def test_get_child_assignations(self):
        print(f"\nTEST START:{self._testMethodName}")
        # make multiple child items and assign them
        handler = CategoryHandler(self.prj)
        num_child = 10
        for i in range(num_child):
            topic_name = f"test_subtopic-{get_micro_time()}"
            child_prj = Category.objects.create(category_creator=self.authors[0], category_name=topic_name)
            handler.add_child_category(child_prj)

        children = handler.get_child_assignations()
        self.assertEqual(num_child, len(children))
        for c in children:
            self.assertIsInstance(c, CategoryItemAssignation)

    def test_get_child_items(self):
        print(f"\nTEST START:{self._testMethodName}")
        # make multiple child items and assign them
        handler = CategoryHandler(self.prj)
        num_child = 10
        for i in range(num_child):
            topic_name = f"test_subtopic-{get_micro_time()}"
            child_prj = Category.objects.create(category_creator=self.authors[0], category_name=topic_name)
            handler.add_child_category(child_prj)

        children = handler.get_child_items()
        self.assertEqual(num_child, len(children))
        for c in children:
            self.assertIsInstance(c, CategoryItem)

    def test_move_child_item_forward(self):
        print(f"\nTEST START:{self._testMethodName}")
        # make multiple child items and assign them
        handler = CategoryHandler(self.prj)
        num_child = 10
        for i in range(num_child):
            topic_name = f"test_subtopic-{i}"
            child_prj = Category.objects.create(category_creator=self.authors[0], category_name=topic_name)
            handler.add_child_category(child_prj)
        child_items = handler.get_child_items()
        move_i = child_items[0]
        move_a_id = CategoryItemAssignation.objects.get(item_id=move_i.item_id).item_assignation_id

        new_pos = 5
        all_a = handler.get_child_assignations()
        # print(all_a)
        handler.move_child_item(child_item=move_i, new_pos=new_pos)

        all_a = handler.get_child_assignations()
        child_items = handler.get_child_items()
        # print(all_a)
        new_i = child_items[new_pos-1]
        new_a = CategoryItemAssignation.objects.get(item_id=new_i.item_id)
        self.assertEqual(move_a_id,  new_a.item_assignation_id)
        self.assertEqual(len(all_a), num_child)
        self.assertEqual(new_a.position, new_pos-1)  # -1 because positions are 0 indexed
        all_a = handler.get_child_assignations()
        for i in range(len(all_a)):
            self.assertIsInstance(all_a[i], CategoryItemAssignation)
            self.assertEqual(all_a[i].position, i)

    def test_move_child_item_backward(self):
        print(f"\nTEST START:{self._testMethodName}")
        # make multiple child items and assign them
        handler = CategoryHandler(self.prj)
        num_child = 10
        for i in range(num_child):
            topic_name = f"test_subtopic-{i}"
            child_prj = Category.objects.create(category_creator=self.authors[0], category_name=topic_name)
            handler.add_child_category(child_prj)
        child_items = handler.get_child_items()
        move_i = child_items[9]
        move_a_id = CategoryItemAssignation.objects.get(item_id=move_i.item_id).item_assignation_id

        new_pos = 5
        handler.move_child_item(child_item=move_i, new_pos=new_pos)

        all_a = handler.get_child_assignations()
        child_items = handler.get_child_items()
        # print(all_a)
        new_i = child_items[new_pos - 1]
        new_a = CategoryItemAssignation.objects.get(item_id=new_i.item_id)
        self.assertEqual(move_a_id, new_a.item_assignation_id)
        self.assertEqual(len(all_a), num_child)
        self.assertEqual(new_a.position, new_pos - 1)  # -1 because positions are 0 indexed
        all_a = handler.get_child_assignations()
        for i in range(len(all_a)):
            self.assertIsInstance(all_a[i], CategoryItemAssignation)
            self.assertEqual(all_a[i].position, i)

    def test_move_child_item_to_same(self):
        print(f"\nTEST START:{self._testMethodName}")
        # make multiple child items and assign them
        handler = CategoryHandler(self.prj)
        num_child = 10
        for i in range(num_child):
            topic_name = f"test_subtopic-{i}"
            child_prj = Category.objects.create(category_creator=self.authors[0], category_name=topic_name)
            handler.add_child_category(child_prj)
        child_items = handler.get_child_items()
        move_i = child_items[4]
        old_move_a = CategoryItemAssignation.objects.get(item_id=move_i.item_id)

        new_pos = 5
        handler.move_child_item(child_item=move_i, new_pos=new_pos)

        all_a = handler.get_child_assignations()
        child_items = handler.get_child_items()
        # print(all_a)
        new_i = child_items[new_pos - 1]
        new_a = CategoryItemAssignation.objects.get(item_id=new_i.item_id)
        self.assertEqual(old_move_a.item_assignation_id, new_a.item_assignation_id)
        self.assertEqual(len(all_a), num_child)
        self.assertEqual(new_a.position, new_pos - 1)  # -1 because positions are 0 indexed
        all_a = handler.get_child_assignations()
        for i in range(len(all_a)):
            self.assertIsInstance(all_a[i], CategoryItemAssignation)
            self.assertEqual(all_a[i].position, i)

    def test_move_child_item_to_less_than_lower_bond(self):
        print(f"\nTEST START:{self._testMethodName}")
        # make multiple child items and assign them
        handler = CategoryHandler(self.prj)
        num_child = 10
        for i in range(num_child):
            topic_name = f"test_subtopic-{i}"
            child_prj = Category.objects.create(category_creator=self.authors[0], category_name=topic_name)
            handler.add_child_category(child_prj)
        child_items = handler.get_child_items()
        move_i = child_items[4]
        with self.assertRaises(ValueError):
            # first checks boundary value before adjusting to 0 index (-1)
            handler.move_child_item(child_item=move_i, new_pos=0)

    def test_move_child_item_to_more_than_upper_bound(self):
        print(f"\nTEST START:{self._testMethodName}")
        # make multiple child items and assign them
        handler = CategoryHandler(self.prj)
        num_child = 10
        for i in range(num_child):
            topic_name = f"test_subtopic-{i}"
            child_prj = Category.objects.create(category_creator=self.authors[0], category_name=topic_name)
            handler.add_child_category(child_prj)
        child_items = handler.get_child_items()
        move_i = child_items[4]
        with self.assertRaises(ValueError):
            handler.move_child_item(child_item=move_i, new_pos=num_child+1)

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
        proj = CategoryHandler.create_project(self.authors[0])
        topic = CategoryHandler.create_project(self.authors[0])
        subtopic = CategoryHandler.create_project(self.authors[0])
        CategoryHandler(proj).add_child_category(topic)
        self.main_handler.publish_article(topic)
        topic_handler = CategoryHandler(topic)
        topic_handler.add_child_category(subtopic)
        topic_handler.get_child_articles()
        self.assertEqual(1, len(topic_handler.get_child_articles()))
        self.assertEqual(2, len(topic_handler.get_child_assignations()))

    def test_publish_article_to_as_child_article(self):
        print(f"\n{self._testMethodName}")
        proj = CategoryHandler.create_project(self.authors[0])
        topic = CategoryHandler.create_project(self.authors[0])
        CategoryHandler(proj).add_child_category(topic)
        parent_article = ArticleHandler.create_new_article(self.authors[0]).article
        print(parent_article.article_id)
        item = CategoryItem.objects.get(item_article_id=parent_article.article_id)
        print(f"ITEM: {item}")
        ArticleHandler(parent_article).publish_article(topic)

        handler = ArticleHandler.create_new_article(self.authors[0])
        handler.publish_as_child_article(parent_article)
        topic_handler = CategoryHandler(topic)
        topic_handler.get_child_articles()
        self.assertEqual(2, len(topic_handler.get_child_articles()))
        self.assertEqual(2, len(topic_handler.get_child_assignations()))

    def test_publish_article_to_project_raises_exception(self):
        print(f"\n{self._testMethodName}")
        proj = CategoryHandler.create_project(self.authors[0])
        handler = ArticleHandler.create_new_article(self.authors[0])
        with self.assertRaises(ValueError):
            handler.publish_article(proj)

    def test_draft_article(self):
        print(f"\n{self._testMethodName}")
        proj = CategoryHandler.create_project(self.authors[0])
        topic = CategoryHandler.create_project(self.authors[0])
        CategoryHandler(proj).add_child_category(topic)
        topic_handler = CategoryHandler(topic)
        self.main_handler.publish_article(topic)
        self.assertEqual(len(topic_handler.get_child_assignations()), 1)
        self.assertEqual(len(topic_handler.get_child_articles()), 1)
        self.main_handler.draft_article()
        self.assertEqual(len(topic_handler.get_child_articles()), 0)

    def test_get_parent_article_returns_none(self):
        print(f"\n{self._testMethodName}")
        parent = ArticleHandler(self.main_article).get_parent_article()
        self.assertIsNone(parent)

    @skip("TODO")
    def test_get_parent_article(self):
        print(f"\n{self._testMethodName}")
        # handler =
        pass

    @skip("TODO")
    def test_get_child_article_returns_none(self):
        print(f"\n{self._testMethodName}")
        pass

    @skip("TODO")
    def test_get_child_article(self):
        print(f"\n{self._testMethodName}")
        pass
