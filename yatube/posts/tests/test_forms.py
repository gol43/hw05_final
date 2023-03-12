from posts.models import Post, Group, User, Comment
from django.test import Client, TestCase, override_settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from http import HTTPStatus
import shutil
import tempfile
from django.conf import settings
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
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
        cls.group_v2_for_check = Group.objects.create(
            title='Тестовый заголовок для проверки',
            slug='Test-dlya-slug-for-proverki',
            description='Тестовый заголовок для проверки')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """проверка формы для поста"""
        tasks_count = Post.objects.count() + 1
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id, }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,)
        self.assertRedirects(
            response, reverse('posts:profile',
                              args=[get_object_or_404(User,
                                                      username='gol43')]))
        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertTrue(Post.objects.filter(group=self.group,
                                            text='Тестовый текст',).exists())

    def test_edit_post(self):
        """проверка редакции"""
        form_data = {
            'text': 'Тестовый текст из формы для проверки',
            'group': self.group_v2_for_check.id}
        response = self.authorized_client.post(
            reverse('posts:edit_post',
                    kwargs={'post_id': f'{self.post.id}'}),
            data=form_data, follow=True,)
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': f'{self.post.id}'}))
        self.assertTrue(Post.objects.filter(
                        text='Тестовый текст из формы для проверки',
                        group=self.group_v2_for_check.id
                        ).exists())
        self.assertFalse(Post.objects.filter(
                         text='Тестовый текст из формы',
                         group=self.group.id
                         ).exists())

    def test_cant_create_existing_slug(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст из формы',
            'title': 'Тестовый заголовок из формы',
            'group': self.group, }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_guest_user_cant_create_and_edit_posts(self):
        """тесты для неавторизованного пользователя,
          который хочет создать или отредачить пост"""
        form_urls = [
            reverse('posts:post_create'),
            reverse('posts:edit_post', kwargs={'post_id': self.post.pk}), ]
        for form_url in form_urls:
            with self.subTest(form_url):
                response = self.guest_client.post(
                    form_url,
                    data={'text': 'Тестовый текст из формы для проверки',
                          'group': self.group_v2_for_check.id, })
                self.assertIn('/auth/login/', response.url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertFalse(Post.objects.filter(
                    group=self.group,
                    text={'Тестовый текст из формы'},).exists())


class CommentTest(TestCase):
    def test_comment(self):
        user = User.objects.create_user(username='gol43')
        authorized_client = Client()
        authorized_client.force_login(user)
        group = Group.objects.create(
            title='Тестовый заголовок',
            slug='Test-dlya-slug',
            description='Тестовое описание')
        post = Post.objects.create(
            text='Тестовый текст',
            author=user,
            group=group,)
        comment = Comment.objects.create(
            text='Тестовый текст для комментария',
            author=user,
            post=post,)
        form_data = {'text': comment}
        response = authorized_client.get(reverse('posts:post_detail',
                                         kwargs={'post_id': post.id}),
                                         data=form_data,
                                         folow=True)
        newbee_commets = Comment.objects.get(id=post.id)
        self.assertContains(response, 'Тестовый текст для комментария')
        information_for_subtest = {
            comment.text: newbee_commets.text,
            user: newbee_commets.author}
        for info_v1, info_v2 in information_for_subtest.items():
            with self.subTest(value=info_v1):
                self.assertEqual(info_v1, info_v2)
        # assertContains(response, text, ...) проверяет,
        # что в ответе сервера содержится указанный текст;
