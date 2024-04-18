from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("group/<slug:slug>/", views.group_posts, name="group_posts"),
    path("new/", views.new_post, name="new_post"),
    # Профайл пользователя
    path('posts/<str:username>/', views.profile, name='profile'),
    # Просмотр записи
    path('posts/<str:username>/<int:post_id>/', views.post_view, name='post'),
    path(
        'posts/<str:username>/<int:post_id>/edit/', 
        views.post_edit, 
        name='post_edit'
        ),
    path('follow-unfollow/', views.follow_unfollow, name='follow_unfollow'),
    path("<username>/<int:post_id>/comment", views.add_comment, name="add_comment"),

]