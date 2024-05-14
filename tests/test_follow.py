import pytest

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import User, Post, Group, Follow
from django.db.models import fields
from django.core.cache import cache
from django.urls import reverse

try:
    from posts.models import Follow
except ImportError:
    assert False, 'Не найдена модель Follow'

try:
    from posts.models import Post
except ImportError:
    assert False, 'Не найдена модель Post'

def search_field(fields, attname):
    for field in fields:
        if attname == field.attname:
            return field
    return None

def search_refind(execution, user_code):
    """Поиск запуска"""
    for temp_line in user_code.split('\n'):
        if re.search(execution, temp_line):
            return True
    return False

class TestFollow(TestCase):

    def test_follow_model(self):
        model_fields = Follow._meta.fields

        user_field = search_field(model_fields, 'user_id')
        assert user_field is not None, 'Добавьте пользователя, автор который создал событие `user` модели `Follow`'
        assert type(user_field) == fields.related.ForeignKey, (
            'Свойство `user` модели `Follow` должно быть ссылкой на другую модель `ForeignKey`'
        )
        assert user_field.related_model == get_user_model(), (
            'Свойство `user` модели `Follow` должно быть ссылкой на модель пользователя `User`'
        )
        assert user_field.remote_field.related_name == 'follower', (
            'Свойство `user` модели `Follow` должно иметь аттрибут `related_name="follower"`'
        )

        author_field = search_field(model_fields, 'author_id')
        assert author_field is not None, 'Добавьте пользователя, автор который создал событие `author` модели `Follow`'
        assert type(author_field) == fields.related.ForeignKey, (
            'Свойство `author` модели `Follow` должно быть ссылкой на другую модель `ForeignKey`'
        )
        assert author_field.related_model == get_user_model(), (
            'Свойство `author` модели `Follow` должно быть ссылкой на модель пользователя `User`'
        )
        assert author_field.remote_field.related_name == 'following', (
            'Свойство `author` модели `Follow` должно иметь аттрибут `related_name="following"`'
        )



    @pytest.mark.django_db(transaction=True)
    def test_follow_not_auth(self):
        client = Client()
        url = reverse('follow_index')
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == '/auth/login/?next=/follow/', 'Страница `/follow/` работает неправильно'

        url = reverse('profile_follow', args=['test_user'])
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == '/auth/login/?next=/test_user/follow/', 'Страница `/test_user/follow/` работает неправильно'

        url = reverse('profile_unfollow', args=['test_user'])
        response = client.get(url)
        assert response.status_code == 302
        assert response.url == '/auth/login/?next=/test_user/unfollow/', 'Страница `/test_user/unfollow/` работает неправильно'

    @pytest.mark.django_db(transaction=True)
    def test_follow_auth(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.client.force_login(self.user)
        cache.clear()
        self.post = Post.objects.create(author=self.user, text='Some text')
        self.post = Post.objects.create(author=self.user, text='22')
        self.client.logout()

        self.user_2 = User.objects.create_user(username='test_user_2', password='test_password_2')
        self.client.force_login(self.user_2)

        response = self.client.post(reverse('profile_follow', kwargs={'username': 'test_user_2'}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Follow.objects.count(), 0, 'Подписка создалась на самого себя')

        response = self.client.post(reverse('profile_follow', kwargs={'username': 'test_user'}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Follow.objects.count(), 1)
        self.assertTrue(Follow.objects.filter(user=self.user_2, author=self.user).exists(), 'Подписка не создалась')

        response = self.client.get('/follow/')
        self.assertEqual(response.status_code, 200, 'Страница `/follow/` работает неправильно')
        self.assertContains(response, 'Some text', status_code=200, msg_prefix='Страница `/` не содержит поста')
        self.assertEqual(len(response.context.get('page').object_list), 2, 'Нет двух постов')

        response = self.client.get(reverse('profile_unfollow', kwargs={'username': 'test_user'}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Follow.objects.count(), 0)
        self.assertFalse(Follow.objects.filter(user=self.user_2, author=self.user).exists(), 'Подписка не удалилась')

        response = self.client.get('/follow/')
        self.assertEqual(response.status_code, 200, 'Страница `/follow/` работает неправильно')
        self.assertNotContains(response, 'Some text', status_code=200, msg_prefix='Страница `/` содержит пост')