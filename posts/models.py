from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Group(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title

class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, related_name="posts", blank=True, null=True)

    # поле для картинки
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
       # выводим текст поста 
       return self.text

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(help_text="Введите текст комментария", verbose_name="Текст комментария", max_length=500)
    created = models.DateTimeField("date published", auto_now_add=True)

    def __str__(self):
        return self.text

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")