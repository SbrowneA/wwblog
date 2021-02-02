from django.test import TestCase
from wwapp.models import Article
from .model_tests import setup_authors
from wwapp.urls import *

class URLTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.authors = setup_authors()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_edit_not_authorized(self):
        Article.objects.create(author=self.authors[2])
        response = self.client.get('wwapp:',)
        self.client.
        self.assertEqual(response.status_code, 403)

    # def test_browse_category(self):
    # def test_edit_category_page_not_logged_in(self):
    # def test_edit_category_page_when_logged_in(self):

