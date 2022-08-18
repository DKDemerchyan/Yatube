import shutil
import tempfile

from django import forms
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test-slug')
        cls.author = User.objects.create_user(username='test_author')
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст тестового поста автора test_name_one',
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)

    def test_pages_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': self.author}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}): (
                'posts/create_post.html'
            ),
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        """Проверяю контекст index"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        context_objects = {
            self.author.id: first_object.author.id,
            self.post.text: first_object.text,
            self.group.slug: first_object.group.slug,
            self.post.id: first_object.id,
            Post.objects.first().image: first_object.image,
        }
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def test_group_posts_correct_context(self):
        """Проверяю контекст group_posts"""
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        context_objects = {
            self.author.id: first_object.author.id,
            self.post.text: first_object.text,
            self.group.slug: first_object.group.slug,
            self.post.id: first_object.id,
            Post.objects.first().image: first_object.image,
        }
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(reverse_name, response_name)

    def test_profile_correct_context(self):
        """Проверяю контекст profile"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': self.author.username}))
        first_object = response.context['page_obj'][0]
        context_objects = {
            self.author.id: first_object.author.id,
            self.post.text: first_object.text,
            self.group.slug: first_object.group.slug,
            self.post.id: first_object.id,
            Post.objects.first().image: first_object.image,
        }
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def test_post_detail_correct_context(self):
        """Проверяю контекст post_detail"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        object = response.context['post']
        expected = self.post
        self.assertEqual(object, expected)

    def test_post_edit_correct_context(self):
        """Проверяю контекст post_edit"""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_create_correct_context(self):
        """Проверяю контекст post_create"""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
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
            text='Тестовый текст тестового поста автора test_name_one',)
        cls.posts = []
        for num in range(14):
            Post.objects.create(
                author=cls.author,
                group=cls.group,
                text=f'Пост номер {num}'
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)

    def test_first_page_paginator(self):
        pages = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': self.author}): (
                'posts/profile.html'
            ),
        }
        for reverse_name in pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                posts_qty = len(response.context['page_obj'])
                self.assertEqual(posts_qty, 10)

    def test_second_page_paginator(self):
        pages = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': self.author}): (
                'posts/profile.html'
            ),
        }
        for reverse_name in pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get((reverse_name) + '?page=2')
                posts_qty = len(response.context['page_obj'])
                self.assertEqual(posts_qty, 5)
