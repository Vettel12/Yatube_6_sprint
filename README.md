# Как запустить на ПК

Выбираем, куда будем кланировать (например на диск B в папку TEST_PROJECT)

```bash
cd /B/TEST_PROJECT
```

Клонируем проект:

```bash
git clone https://github.com/Vettel12/Yatube_6_sprint
```

Заходим в директорию проекта:

```bash
cd /Yatube_6_sprint
```

Устанавливаем виртуальное окружение:

```bash
python -m venv venv
```

Активируем виртуальное окружение:

```bash
source venv/Scripts/activate
```

> Для деактивации виртуального окружения выполним (после работы):
> ```bash
> deactivate
> ```

Устанавливаем зависимости:

```bash
python -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```

Применяем миграции:

```bash
python yatube/manage.py makemigrations
python yatube/manage.py migrate
```

Для запуска тестов выполним:

```bash
pytest
```

Получим:

```bash
plugins: Faker-24.14.0, django-4.8.0, pythonpath-0.7.4
collected 20 items

tests/test_404_page.py::Profile::test_404_page PASSED                                                                                   [5%]
tests/test_5.py::Profile::test_nopub_post PASSED                                                                                   [10%]
tests/test_5.py::Profile::test_profile_view PASSED                                                                                   [15%]
tests/test_5.py::Profile::test_pub_post PASSED                                                                                   [20%]
tests/test_6.py::Profile::test_error_format PASSED                                                                                   [25%]
tests/test_6.py::Profile::test_images_post PASSED                                                                                   [30%]
tests/test_cache.py::Profile::test_cache PASSED                                                                                   [35%]
tests/test_comment.py::TestComment::test_comment PASSED                                                                                   [40%]
tests/test_comment.py::TestComment::test_comment_model PASSED                                                                                   [45%] 
tests/test_follow.py::TestFollow::test_follow_auth PASSED                                                                                   [50%]
tests/test_follow.py::TestFollow::test_follow_model PASSED                                                                                   [55%] 
tests/test_follow.py::TestFollow::test_follow_not_auth PASSED                                                                                   [60%] 
tests/test_homework.py::TestPost::test_post_create PASSED                                                                                   [65%]
tests/test_homework.py::TestGroup::test_group_create PASSED                                                                                   [70%]
tests/test_homework.py::TestGroupView::test_group_view PASSED                                                                                   [75%]
tests/test_new.py::TestNewView::test_new_view_get PASSED                                                                                   [80%]
tests/test_new.py::TestNewView::test_new_view_post PASSED                                                                                   [85%]
tests/test_homework.py::TestPost::test_post_model PASSED                                                                                   [90%]
tests/test_homework.py::TestPost::test_post_admin PASSED                                                                                   [95%] 
tests/test_homework.py::TestGroup::test_group_model PASSED                                                                                   [100%] 

=============================================================== 20 passed in 5.06s ================================================================ 
```

Создать суперпользователя:

```bash
python manage.py createsuperuser
```

Запустить проект:

```bash
python manage.py runserver
```

Вот такой должен быть резульат, когда зайдете или зарегистрируетесь:

<img width="1000px" src="https://github.com/Vettel12/Yatube_6_sprint/blob/main/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202024-06-02%20195420.png?raw=true" align="center" alt="GitHub Readme Stats" />

Главная стариница по адресу: http://127.0.0.1:8000/

Страница пользователя по адресу: http://127.0.0.1:8000/posts//<str:username>/

Страница отдельного поста: http://127.0.0.1:8000/posts/<str:username>/<int:post_id>/

Страница избранных авторов: http://127.0.0.1:8000/follow/

Страница группы: http://127.0.0.1:8000/group/<slug:slug>/

Страница админа: http://127.0.0.1:8000/admin/