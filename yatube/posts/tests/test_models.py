from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def test_post_correct_object_names(self):
        """Проверяем, что у post модели корректно работает __str__."""
        post = PostModelTest.post
        self.assertEqual(post.text[:15], str(post))

    def test_group_correct_object_names(self):
        """Проверяем, что у group модели корректно работает __str__"""
        group = PostModelTest.group
        self.assertEqual(group.slug, 'test_slug')

    def test_verbose_names(self):
        """Проверяем верность verbose_name"""
        post = PostModelTest.post
        verboses = {
            'text': 'Текст Вашего поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор поста',
            'group': 'Группа',
        }
        for field, expected in verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected
                )

    def test_help_texts(self):
        post = PostModelTest.post
        help_texts = {
            'text': 'Введите текст',
            'group': 'Группа, к которой относится пост'
        }
        for field, expected in help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected
                )
