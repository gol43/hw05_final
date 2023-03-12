from posts.models import Group, Post
from django.test import Client, TestCase
from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
User = get_user_model()


class PostURLTest(TestCase):
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
        cls.for_all_clients_urls = [
            '/',
            '/group/Test-dlya-slug/',
            '/posts/1/',
            '/profile/gol43/', ]
        cls.for_author_urls = [
            '/posts/1/edit']
        cls.only_for_authorized_clients_urls = [
            '/',
            '/group/Test-dlya-slug/',
            '/posts/1/',
            '/profile/gol43/',
            '/create/',
            '/follow/']

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_detail_url_exists_at_desired_location(self):
        """проверка для всех пользователей."""
        for url in self.for_all_clients_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_home_url_exists_for_author(self):
        """проверка для автора"""
        for url in self.for_author_urls:
            with self.subTest(url=url):
                post_user = get_object_or_404(User, username='gol43')
                if post_user == self.authorized_client:
                    response = self.authorized_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail_url_exists_at_desired_location_authorized(self):
        """проверка для авторизированных пользователей"""
        for url in self.only_for_authorized_clients_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """проверка урлов и шаблонов"""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/Test-dlya-slug/',
            'posts/profile.html': '/profile/gol43/',
            'posts/post_detail.html': '/posts/1/',
            'posts/post_create.html': '/create/',
            'posts/edit_post.html': '/posts/1/edit/',
            'posts/follow.html': '/follow/'}
        for template, urls in templates_url_names.items():
            with self.subTest(address=urls):
                response = self.authorized_client.get(urls)
                self.assertTemplateUsed(response, template)
