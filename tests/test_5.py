import pytest

from django.test import TestCase, Client
from posts.models import User, Post

class Profile(TestCase):
    def setUp(self):
        self.client = Client()

        # Устанавливаем начальные данные для тестов
        try:
            self.user = User.objects.create_user(username='test_user', password='test_password')
        except Exception as e:
            self.fail(f'Не удалось создать пользователя. Ошибка: `{e}`')
        try:
            self.client.force_login(self.user)
        except Exception as e:
            self.fail(f'Не удалось войти в систему. Ошибка: `{e}`')

    def test_profile_view(self):
        # Проверяем, что профиль пользователя доступен
        try:
            response = self.client.get('/posts/test_user/')
        except Exception as e:
            self.fail(f'Страница `/posts/test_user/` работает неправильно. Ошибка: `{e}`')
        self.assertEqual(response.status_code, 200, 'Страница `/posts/test_user/` работает неправильно.')

    def test_pub_post(self):
        # Публикация нового поста пользователем
        try:
            self.post = Post.objects.create(text="You're talking about things I haven't done yet in the past tense. It's driving me crazy!", author=self.user)
        except Exception as e:
            self.fail(f'Не удалось создать пост. Ошибка: `{e}`')
        try:
            response = self.client.get(f'/posts/{self.user.username}/{self.post.id}/')
        except Exception as e:
            self.fail(f'Страница `/posts/{self.user.username}/{self.post.id}/` работает неправильно. Ошибка: `{e}`')
        self.assertEqual(response.status_code, 200, 'Страница `/posts/{self.user.username}/{self.post.id}/` работает неправильно.')
        self.assertEqual(len(response.context["posts"]), 1, 'Страница `/posts/{self.user.username}/{self.post.id}/` работает неправильно.')
        self.assertIsInstance(response.context["user"], User, 'Страница `/posts/{self.user.username}/{self.post.id}/` работает неправильно.')
        self.assertEqual(response.context["user"].username, self.user.username, 'Страница `/posts/{self.user.username}/{self.post.id}/` работает неправильно.')

        # Проверяем, что пост отображается на странице профиля
        try:
            response = self.client.get(f'/posts/{self.user.username}/')
        except Exception as e:
            self.fail(f'Страница `/posts/test_user/` работает неправильно. Ошибка: `{e}`')
        self.assertEqual(response.status_code, 200, 'Страница `/posts/test_user/` работает неправильно.')
        self.assertContains(response, 'You&#x27;re talking about things I haven&#x27;t done yet in the past tense. It&#x27;s driving me crazy!', status_code=200)

        # Проверяем, что пост отображается на главной странице
        try:
            response = self.client.get('/')
        except Exception as e:
            self.fail(f'Страница `/` работает неправильно. Ошибка: `{e}`')
        self.assertEqual(response.status_code, 200, 'Страница `/` работает неправильно.')
        print(response.content.decode('utf-8'))
        self.assertContains(response, 'You&#x27;re talking about things I haven&#x27;t done yet in the past tense. It&#x27;s driving me crazy!', status_code=200)

        # Редактирование поста и проверка обновления текста
        try:
            response = self.client.post(f'/posts/{self.user.username}/{self.post.id}/edit/', {'text': "Новый текст вашего поста"
, 'csrfmiddlewaretoken': '2XM26AIhVOyVIjp907EiNXdXki9qJrdBUn3dn1JQ9Eu9JYxuAclvtjt0L56IfYfR'})
        except Exception as e:
            self.fail(f'Страница `/posts/{self.user.username}/{self.post.id}/edit/` работает неправильно. Ошибка: `{e}`')
        self.assertEqual(response.status_code, 302, 'Страница `/posts/{self.user.username}/{self.post.id}/edit/` работает неправильно.')
        updated_response = self.client.get(f'/posts/{self.user.username}/{self.post.id}/')
        self.assertContains(updated_response, 'Новый текст вашего поста', status_code=200, msg_prefix='Текст поста не обновлен')

    def test_nopub_post(self):
        # Проверяем, что незарегистрированный пользователь не может получить доступ к созданию нового поста
        self.client.logout()

        response = self.client.get('/new/')
        self.assertEqual(response.status_code, 302, 'Страница `/new/` не возвращает код состояния 302.')

        login_url = response.url
        self.assertTrue(login_url.startswith('/auth/login/'), f'Пользователь не перенаправлен на страницу входа. Ожидался URL `/auth/login/`, получен: {login_url}')
        self.assertIn('/new/', login_url, 'URL страницы `/new/` отсутствует в URL страницы входа')