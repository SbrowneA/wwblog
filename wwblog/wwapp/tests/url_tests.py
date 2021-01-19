from django.test import TestCase


class URLTests(TestCase):
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    # def test_browse_category(self):
    # def test_edit_category_page_not_logged_in(self):
    # def test_edit_category_page_when_logged_in(self):

