from django.test import TestCase
from wwapp.models import Article
# from .model_tests import setup_authors,
from wwapp.urls import *
from .setups import setup_authors, setup_superuser
from unittest import skip


class URLTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.authors = setup_authors()
        cls.superuser = setup_superuser()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_article_not_found(self):
        response = self.client.get(f'/post/999/view')
        self.assertEqual(response.status_code, 404)

    def test_edit_not_authorized(self):
        a = Article.objects.create(author=self.authors[2])
        response = self.client.get(f'/post/{a.article_id}/edit')
        # self.client.login()
        # returns 302 (not 403) because they are being redirected to login instead of being blocked
        self.assertEqual(response.status_code, 302)

    def test_login(self):
        pass

    @skip
    def test_create_create_new_article_directory_creates_new_instance(self):
        # login is not correct
        self.client.login(self.superuser.username, password="superuser1")
    # def test_browse_category(self):
    # def test_edit_category_page_not_logged_in(self):
    # def test_edit_category_page_when_logged_in(self):
