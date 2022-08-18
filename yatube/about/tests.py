from http import HTTPStatus

from django.test import Client, TestCase


class AboutPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_available_at_url(self):
        """About недоступен по нужному адресу"""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_use_template(self):
        """About использует неверный шаблон"""
        response = self.guest_client.get('/about/author/')
        self.assertTemplateUsed(response, 'about/author.html')

    def test_tech_available_at_url(self):
        """Tech недоступен по нужному адресу"""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech_use_template(self):
        """Tech использует неверный шаблон"""
        response = self.guest_client.get('/about/tech/')
        self.assertTemplateUsed(response, 'about/tech.html')
