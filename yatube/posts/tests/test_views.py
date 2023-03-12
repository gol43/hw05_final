from posts.models import Group, Post, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django import forms
from django.conf import settings
import shutil
import tempfile
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='gol43')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='Test-dlya-slug',
            description='Тестовое описание')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """проверка шаблона"""
        templates_pages_names = {
            'posts/index.html':
            (reverse('posts:index')),
            'posts/group_list.html':
            (reverse('posts:group_posts',
                     kwargs={'slug': 'Test-dlya-slug'})),
            'posts/profile.html':
            reverse('posts:profile',
                    args=[get_object_or_404(User, username='gol43')]),
            'posts/post_detail.html':
            (reverse('posts:post_detail',
                     kwargs={'post_id': self.post.pk})),
            'posts/edit_post.html':
            reverse('posts:edit_post',
                    kwargs={'post_id': self.post.pk}),
            'posts/post_create.html':
            reverse('posts:post_create'), }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """проверка контекста у индекса"""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        post_object = response.context['page_obj'][0]
        author = post_object.author
        group = post_object.group
        text = post_object.text
        self.assertEqual(author, self.user)
        self.assertEqual(group, self.post.group)
        self.assertEqual(text, self.post.text)

    def test_group_posts_pages_show_correct_context(self):
        """проверка контекста у групп пост"""
        response = self.guest_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': 'Test-dlya-slug'}))
        post_object = response.context['group']
        slug = post_object.slug
        title = post_object.title
        description = post_object.description
        self.assertEqual(slug, self.group.slug)
        self.assertEqual(title, self.group.title)
        self.assertEqual(description, self.group.description)
        self.assertIn('group', response.context)

    def test_post_detail_page_show_correct_context(self):
        """проверка контекста у пост дитейл"""
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context['post'], self.post)

    def test_profile_page_show_correct_context(self):
        """проверка контекста у профайла"""
        response = self.guest_client.get(reverse(
            'posts:profile', kwargs={'username': 'gol43'}))
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(response.context['page_obj'][0].text,
                         'Тестовый текст')
        self.assertEqual(response.context['page_obj'][0].author.username,
                         'gol43')
        self.assertEqual(response.context['page_obj'][0].group.title,
                         'Тестовый заголовок')

    def test_edit_post_page_show_correct_context(self):
        """проверка контекста у пост эдит"""
        response = self.authorized_client.get(reverse('posts:edit_post',
                                                      kwargs={'post_id':
                                                              self.post.pk}))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField, }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_show_correct_context(self):
        """проверка контекста у криейт поста"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField, }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    """проверка пагинатора"""
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='gol43')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='Test-dlya-slug',
            description='Тестовое описание')
        bilk_post: list = []
        for i in range(13):
            bilk_post.append(Post(text=f'Тестовый текст {i}',
                                  group=self.group,
                                  author=self.user))
        Post.objects.bulk_create(bilk_post)

    def test_first_page_index_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_index_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_group_posts_contains_ten_records(self):
        response = self.client.get(reverse('posts:group_posts',
                                           kwargs={'slug': 'Test-dlya-slug'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_posts_contains_three_records(self):
        response = self.client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': 'Test-dlya-slug'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_profile_contains_ten_records(self):
        response = self.client.get(reverse(
            'posts:profile',
            args=[get_object_or_404(User, username='gol43')]))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_profile_contains_three_records(self):
        response = self.client.get(reverse(
            'posts:profile',
            args=[get_object_or_404(User, username='gol43')]) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageExsitsContext(TestCase):
    @classmethod
    def setUpclass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='fol43')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='fol43')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif')
        self.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='Test-dlya-slug',
            description='Тестовое описание')
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
            image=self.uploaded,)

    def test_image_for_urls_index_gp_profile(self):
        urls_which_have_image = {
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': 'Test-dlya-slug'}),
            reverse('posts:profile', kwargs={'username': 'fol43'}), }
        for exptected_values in urls_which_have_image:
            with self.subTest(post=exptected_values):
                response = self.guest_client.get(exptected_values)
        image = response.context['page_obj'][0].image.name
        self.assertEqual(self.post.image.name, image)

    def test_additional_test_for_postdetail(self):
        additional_response_postdetail = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        image_for_detail = (
            additional_response_postdetail.context['post'].image.name)
        self.assertIn(self.post.image.name, image_for_detail)
