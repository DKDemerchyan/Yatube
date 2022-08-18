from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test-slug')
        cls.author = User.objects.create_user(username='test_author')
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст тестового поста автора test_name_one',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)

    def test_public_pages(self):
        """Страницы Главная, Группа, Профиль пользователя,
           Страница поста - доступны всем"""
        url_names = (
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.author}/',
            f'/posts/{self.post.pk}/',
        )
        for address in url_names:
            with self.subTest():
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_is_for_authorised(self):
        """Страница Создания поста доступна авторизированному"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_for_author(self):
        """Редактирование поста доступно лишь автору"""
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_404(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
