from django.db import models, IntegrityError
from django.core import exceptions
from .models import *
# from .models import Category, CategoryItemAssignation, CategoryItem, Article

#
# class CategoryHandler:
#     def __init__(self, parent):
#         self.category = parent
#
#     def get_parent_category(self):
#         try:
#             i = CategoryItem.objects.get(item_category_id=self.category.category_id)
#             return _CategoryItemHandler(i).get_parent_category()
#         except exceptions.ObjectDoesNotExist:
#             raise exceptions.ObjectDoesNotExist
#
#     def get_parent_category_name(self):
#         try:
#             return self.get_parent_category().category_name
#         except exceptions.ObjectDoesNotExist:
#             return ""
#
#     def get_item_assignations(self):
#         try:
#             return CategoryItemAssignation.objects.filter(parent_category_id=self.category.category_id)
#         except exceptions.EmptyResultSet:
#             raise exceptions.EmptyResultSet
#
#     def get_items(self):
#         try:
#             assignations = self.get_item_assignations()
#             items = []
#             for a in assignations:
#                 item = CategoryItem.objects.get(item_id=a.item_id)
#                 items.append(item)
#             return items
#         except exceptions.ObjectDoesNotExist:
#             return []
#
#     def get_child_categories(self):
#         items = self.get_items()
#         sub_cats = []
#         for i in items:
#             if i.item_category_id is not None:
#                 sub_cat = Category.objects.get(category_id=i.item_category_id)
#                 sub_cats.append(sub_cat)
#         return sub_cats
#
#     def get_child_articles(self):
#         items = self.get_items()
#         articles = []
#         for i in items:
#             if i.item_article_id is not None:
#                 a = Article.objects.get(article_id=i.item_article_id)
#                 articles.append(a)
#         return articles
#
#     def get_category_editors(self):
#         try:
#             # TODO make sure working correctly
#             editors = CategoryEditor.objects.filter(category_id=self.category.category_id)
#             if len(editors) != 0:
#                 return editors
#             return []
#         except exceptions.ObjectDoesNotExist:
#             return []
#
#     def get_child_assignations(self):
#         """gets all the child assignations ordered by position"""
#         try:
#             a_list = CategoryItemAssignation.objects.filter(
#                 parent_category_id=self.category.category_id).order_by('position')
#         except exceptions.EmptyResultSet:
#             a_list = []
#         return a_list
#
#     def add_child_item(self, child_item):
#         last_pos = len(self.get_child_assignations())
#         try:
#             # get item assignation and assign parent to self
#             a = CategoryItemAssignation.objects.get(item_id=child_item.item_id)
#             if a.parent_category_id == self.category.category_id:
#                 print("This item has already been assigned to the parent category, try moving it instead")
#             else:
#                 a.parent_category_id = self.category.category_id
#                 a.position = last_pos
#                 a.save()
#         except exceptions.ObjectDoesNotExist:
#             # make new assignation with parent as self
#             a = CategoryItemAssignation(parent_category_id=self.category.category_id, item=child_item,
#                                         position=last_pos)
#             a.save()
#
#         # def add_child_article(self):
#         # TODO needed if PROJECT cant contain articles
#
#     def add_child_category(self, child_cat):
#         if self.category.category_type is not Category.CategoryType.SUBTOPIC:
#             if self.category.category_type is Category.CategoryType.PROJECT:
#                 child_cat.category_type = Category.CategoryType.TOPIC
#                 child_cat.save()
#             elif self.category.category_type is Category.CategoryType.TOPIC:
#                 child_cat.category_type = Category.CategoryType.SUBTOPIC
#                 child_cat.save()
#             child_cat.save()  # save child_cat to make its category item
#             i = CategoryItem.objects.get(item_category_id=child_cat.category_id)
#
#             child_cat.save()
#             self.add_child_item(i)
#         else:
#             raise ValueError("This Category is invalid")
#
#     def __set_assignation_position(self, old_pos, new_pos):
#         a = CategoryItemAssignation.objects.get(parent_category_id=self.category.category_id, position=old_pos)
#         a.position = new_pos
#         a.save()
#
#     def move_child_item(self, child_item, new_pos):
#         try:
#             if new_pos >= 0:
#                 raise ValueError("Position new must be greater than 0")
#             assignations = self.get_child_assignations()
#             moving_a = CategoryItemAssignation.objects.get(item=child_item)
#             old_pos = moving_a.position
#             new_pos -= 1
#             # assign temp position for CategoryItemAssignation being moved
#             moving_a.position = len(assignations)
#             moving_a.save()
#             if new_pos > old_pos:
#                 for i in range(old_pos, new_pos + 1):
#                     self.__set_assignation_position(i, i - 1)
#             elif new_pos < old_pos:
#                 for i in range(old_pos, new_pos - 1, -1):
#                     self.__set_assignation_position(i, i + 1)
#             else:
#                 print("Item was not moved")
#
#             moving_a.position = new_pos
#             moving_a()
#         except exceptions.ObjectDoesNotExist:
#             raise exceptions.ObjectDoesNotExist("Category.move_child_item() "
#                                                 "-> ObjectDoesNotExist: Unexpected Error occurred")
#
#     def delete_child_assignation(self, child_item):
#         pos = child_item.position
#         assignations = self.get_child_assignations()
#         del_a = _CategoryItemHandler(child_item).get_assignation()
#         del_a.delete()
#         for i in range(pos + 1, len(assignations)):
#             a = assignations[i]
#             a.position = a.position - 1
#             a.save()
#
#     def delete_child_category(self, del_cat):
#         # TODO check if sub cats
#         #  delete sub cats & articles
#         # check sub items
#         child_handler = CategoryHandler(del_cat)
#         child_items = child_handler.get_items()
#         if len(child_items) > 0:
#             # delete child items
#             pass
#
#     def transfer_child_items(self, new_category):
#         # TODO
#         # new_category
#         # loop through all articles in old cat
#         # and assign it to the new category
#         pass
#
#     def draft_child_articles(self):
#         articles = self.get_child_articles()
#         for a in articles:
#             a_handler = ArticleHandler(a)
#             a_handler.draft_article()
#
#
# class ArticleHandler:
#     def __init__(self, article):
#         self.article = article
#
#     def get_category_item(self):
#         return CategoryItem.objects.get(item_article_id=self.article.article_id)
#
#     def get_parent_category(self):
#         try:
#             return _CategoryItemHandler(self.get_category_item()).get_parent_category()
#         except exceptions.ObjectDoesNotExist:
#             raise exceptions.ObjectDoesNotExist
#
#     def draft_article(self):
#         pass
#         # try:
#         #     cat = self.get_parent_category()
#         #     c_handler = CategoryHandler(cat)
#         #     c_handler.delete_child_assignation(self.get_category_item())
#         #     self.article.published = False
#         #     self.article.save()
#         # except exceptions.ObjectDoesNotExist:
#         #     raise exceptions.ObjectDoesNotExist("This article is already drafted")
#
#     def publish_article(self, category):
#         pass
#         # item = self.get_category_item()
#         # i_handler = _CategoryItemHandler(item)
#         # try:
#         #     a = i_handler.get_assignation()
#         #     a.parent_category_id = category.category_id
#         #     a.save()
#         # except exceptions.ObjectDoesNotExist:
#         #     cat_handler = CategoryHandler(category)
#         #     cat_handler.add_child_item(item)
#         #
#         # self.article.published = True
#         # self.article.save()
#
#     def add_editor(self, user):
#         try:
#             if user.user_id == self.article.author_id:
#                 raise exceptions.ValidationError("This author is already the creator and editor of the article")
#             else:
#                 editor = ArticleEditor(editor_id=user.user_id, article=self.article)
#                 editor.save()
#         except IntegrityError:
#             raise IntegrityError("This author is already and editor on this article")
#
#     def remove_editor(self, user):
#         """remove an article editor from a user object"""
#         try:
#             if user.user_id == self.article.author_id:
#                 raise exceptions.ValidationError("The creator of the article cannot be removed")
#             else:
#                 editor = self.get_editor(user)
#                 editor.delete()
#         except exceptions.ObjectDoesNotExist:
#             raise exceptions.ObjectDoesNotExist("This author is not an editor on this article or they are the creator")
#         except exceptions.ValidationError:
#             raise exceptions.ValidationError("The creator of the article cannot be removed")
#
#     def get_editors(self):
#         # try:
#             editors = ArticleEditor.objects.filter(article_id=self.article.article_id)
#             if len(editors) == 0:
#                 raise exceptions.EmptyResultSet("This article has no editors")
#             return editors
#         # except exceptions.EmptyResultSet:
#             # raise exceptions.EmptyResultSet("This article has no editors")
#             # raise exceptions.EmptyResultSet()
#
#     def get_parent_article(self):
#         pass
#         return []
#         # TODO
#         # try:
#         #     return Article.objects.get(article_id=self.article.parent_id)
#         # except exceptions.ObjectDoesNotExist:
#         #     raise exceptions.ObjectDoesNotExist
#
#
#     def get_child_article(self):
#         pass
#         return []
#
#     def get_article_group(self):
#         pass
#         articles = [self.article]
#         # get children
#         try:
#             a = self.article
#             while True:
#                 child = ArticleHandler(a).get_child_article()
#                 articles.append(child)
#                 a = child
#         except exceptions.ObjectDoesNotExist:
#             pass
#
#         # get parents
#         try:
#             a = self.article
#             while True:
#                 parent = ArticleHandler(a).get_parent_article()
#                 articles.insert(0, parent)
#                 a = parent
#         except exceptions.ObjectDoesNotExist:
#             pass
#
#         if len(articles) == 1:
#             raise exceptions.ObjectDoesNotExist
#         return articles
#
#     def get_editor(self, user):
#         try:
#             return ArticleEditor.objects.get(editor_id=user.user_id, article_id=self.article.article_id)
#         except exceptions.ObjectDoesNotExist:
#             raise exceptions.ObjectDoesNotExist
#
#     @staticmethod
#     def get_latest_articles(count):
#         latest_articles = Article.objects.order_by('-pub_date')[:int(count)]
#         return latest_articles
#
#     def get_all_versions(self):
#         pass
#
#     def get_latest_version(self):
#         pass
#
#     def get_article_content(self):
#         self.get_latest_version()
#         pass
#
# class _CategoryItemHandler:
#     def __init__(self, item):
#         self.item = item
#
#     def get_assignation(self):
#         pass
#         # try:
#         #     return CategoryItemAssignation.objects.get(item_id=self.item.item_id)
#         # except exceptions.ObjectDoesNotExist:
#         #     raise exceptions.ObjectDoesNotExist
#
#     def get_parent_category(self):
#         pass
#         # try:
#         #     a = self.get_assignation()
#         #     return Category.objects.get(parent_category_id=a.parent_category_id)
#         # except exceptions.ObjectDoesNotExist:
#         #     raise exceptions.ObjectDoesNotExist(
#         #         f"{self.__class__.__name__} => This CategoryItem has no parent assigned")
