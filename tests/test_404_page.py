import pytest

from django.test import TestCase, Client

class Profile(TestCase):
    def setUp(self):
        self.client_1 = Client()

    def test_404_page(self):

        response = self.client_1.get('/L')
        print(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 404, 'Страница `/L` работает неправильно.')
        self.assertContains(response, 'Ошибка 404', status_code=404, msg_prefix='Неверный статус-код страницы 404')