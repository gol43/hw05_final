from ..models import Group, Post, Comment, Follow
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='gol43')
        cls.author_for_check = User.objects.create_user(username='fol43')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='Test-dlya-slug',
            description='Тестовое описание')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,)
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author_for_check,
            text='Тестовый текст для комментария')

    def test_models_have_correct_object_names(self):
        """проверка str"""
        data_for_post = {
            PostModelTest.post: PostModelTest.post.text,
            PostModelTest.group: PostModelTest.group.title,
            PostModelTest.comment: PostModelTest.comment.text, }
        for key, value in data_for_post.items():
            with self.subTest(key=key):
                self.assertEqual(value, str(key))


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='gol43')
        cls.author_for_check = User.objects.create_user(username='fol43')
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author_for_check,)

    def test_for_FollowModel_which_have_correact_objects(self):
        self.assertTrue(Follow.objects.get(author=self.author_for_check,
                                           user=self.user))
