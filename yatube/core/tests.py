from django.test import Client, TestCase


class CorePagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404_use_template(self):
        """Страница 404 использует неверный шаблон"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_403_use_template(self):
        """Страница 403 использует неверный шаблон"""
        response = self.guest_client.get('')
        self.assertTemplateUsed(response, 'core/403csrf.html')
