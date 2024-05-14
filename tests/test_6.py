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
        self.post = Post.objects.create(author=self.user, text='Some text', group=self.group_instance)
        self.post_id = self.post.id
        with open('tests/test.jpeg', 'rb') as img:
            self.post = self.client.post(f'/posts/{self.user.username}/{self.post.id}/edit/', 
                                  {'text': 'post with image', 'image': img, 'group': self.group_instance.id,
                                   'csrfmiddlewaretoken': '2XM26AIhVOyVIjp907EiNXdXki9qJrdBUn3dn1JQ9Eu9JYxuAclvtjt0L56IfYfR'})

    def test_images_post(self):
        response = self.client.get('/')
        self.assertContains(response, '<img', status_code=200, msg_prefix='Страница `/` не содержит картинок')
        response_2 = self.client.get(f'/posts/{self.user.username}/')
        self.assertContains(response_2, '<img', status_code=200, msg_prefix='Страница `/posts/{self.user.username}/` не содержит картинок')
        response_3 = self.client.get(f'/posts/{self.user.username}/{self.post_id}/')
        self.assertContains(response_3, '<img', status_code=200, msg_prefix='Страница `/posts/{self.user.username}/{self.post.id}/` не содержит картинок')
        response_4 = self.client.get(f'/group/{self.group_instance}/')
        self.assertContains(response_4, '<img', status_code=200, msg_prefix='Страница `/posts/{self.user.username}/{self.group_instance}/` не содержит картинок')

    def test_error_format(self):
        self.post_2 = Post.objects.create(author=self.user, text='No', group=self.group_instance)
        self.post2_id = self.post_2.id
        with open('tests/Test.txt', 'rb') as txt:
            self.post_2 = self.client.post(f'/posts/{self.user.username}/{self.post_2.id}/edit/', 
                                  {'text': 'post with image', 'image': txt, 'group': self.group_instance.id,
                                   'csrfmiddlewaretoken': '2XM26AIhVOyVIjp907EiNXdXki9qJrdBUn3dn1JQ9Eu9JYxuAclvtjt0L56IfYfR'})
        response = self.client.get(f'/posts/{self.user.username}/{self.post2_id}/')
        self.assertNotContains(response, '<img', status_code=200, msg_prefix='Позволяет загружать другой формат (не jpeg)')