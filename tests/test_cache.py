import pytest

from django.test import TestCase, Client
from posts.models import User, Post, Group
from django.core.cache import cache

class Profile(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='test_user', password='test_password')
        self.client.force_login(self.user)
        self.group_instance = Group.objects.create(id=1, title='Test', slug='Test', description='Test')
        cache.clear()
        self.post = Post.objects.create(author=self.user, text='Some text', group=self.group_instance)

    def test_cache(self):
        response = self.client.get('/')
        self.assertContains(response, 'Some text', status_code=200, msg_prefix='Страница `/` не содержит поста')
        self.post.delete()
        response_2 = self.client.get('/')
        self.assertContains(response_2, 'Some text', status_code=200, msg_prefix='Страница `/` не содержит поста')
        cache.clear()
        response_3 = self.client.get('/')
        self.assertNotContains(response_3, 'Some text', status_code=200, msg_prefix='Страница `/` содержит пост')