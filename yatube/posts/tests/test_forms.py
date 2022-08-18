from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test-slug'
        )
        cls.author = User.objects.create_user(username='test_author')
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Текст 1'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)

    def test_post_create(self):
        """Запись не создается в БД"""
        posts_count = Post.objects.count()
        form_data = {
            'title': 'Заголовок для тестовой группы',
            'text': 'Текст 2',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.post.author}))
        self.assertEqual(Post.objects.count(), (posts_count + 1))
        self.assertTrue(
            Post.objects.filter(
                text='Текст 2',
            ).exists()
        )

    def test_post_edit(self):
        """Запись в БД не изменяется"""
        form_data = {
            'text': 'Текст 1',
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
            ).exists()
        )

    def test_guest_cant_post_create(self):
        """Гость создаёт новый пост"""
        posts_count = Post.objects.count()
        form_data = {
            'title': 'Заголовок для тестовой группы',
            'text': 'Текст 2',
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        link_login = reverse('users:login')
        link_post_create = reverse('posts:post_create')
        self.assertRedirects(
            response, (f'{link_login}?next={link_post_create}')
        )
        self.assertEqual(Post.objects.count(), posts_count)
