import pytest

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import User, Post, Group
from django.db.models import fields
from django.core.cache import cache
from django.urls import reverse

try:
    from posts.models import Comment
except ImportError:
    assert False, 'Не найдена модель Comment'

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

class TestComment(TestCase):

    def test_comment_model(self):
        model_fields = Comment._meta.fields
        text_field = search_field(model_fields, 'text')
        assert text_field is not None, 'Добавьте название события `text` модели `Comment`'
        assert type(text_field) == fields.TextField, (
            'Свойство `text` модели `Comment` должно быть текстовым `TextField`'
        )

        created_field = search_field(model_fields, 'created')
        assert created_field is not None, 'Добавьте дату и время проведения события `created` модели `Comment`'
        assert type(created_field) == fields.DateTimeField, (
            'Свойство `created` модели `Comment` должно быть датой и время `DateTimeField`'
        )
        assert created_field.auto_now_add, 'Свойство `created` модели `Comment` должно быть `auto_now_add`'

        author_field = search_field(model_fields, 'author_id')
        assert author_field is not None, 'Добавьте пользователя, автор который создал событие `author` модели `Comment`'
        assert type(author_field) == fields.related.ForeignKey, (
            'Свойство `author` модели `Comment` должно быть ссылкой на другую модель `ForeignKey`'
        )
        assert author_field.related_model == get_user_model(), (
            'Свойство `author` модели `Comment` должно быть ссылкой на модель пользователя `User`'
        )

        post_field = search_field(model_fields, 'post_id')
        assert post_field is not None, 'Добавьте свойство `group` в модель `Comment`'
        assert type(post_field) == fields.related.ForeignKey, (
            'Свойство `group` модели `Comment` должно быть ссылкой на другую модель `ForeignKey`'
        )
        assert post_field.related_model == Post, (
            'Свойство `group` модели `Comment` должно быть ссылкой на модель `Post`'
        )

    @pytest.mark.django_db(transaction=True)
    def test_comment(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.client.force_login(self.user)
        cache.clear()
        self.post = Post.objects.create(author=self.user, text='Some text')
        self.client.logout()

        response = self.client.post(reverse('add_comment', kwargs={'username': self.post.author.username, 'post_id': self.post.id}), data={'text': 'Новый коммент!'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')), 'Проверьте, что неаутентифицированные пользователи перенаправляются на страницу входа')

        self.client.login(username='test_user', password='test_password')
        response = self.client.post(reverse('add_comment', kwargs={'username': self.post.author.username, 'post_id': self.post.id}), data={'text': 'Новый коммент!'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('post', kwargs={'username': self.post.author.username, 'post_id': self.post.id}))
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.get().text, 'Новый коммент!')
        self.assertEqual(self.post.comments.count(), 1)