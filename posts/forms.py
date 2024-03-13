from django.db import models
from django.forms import ModelForm

from .models import Post

class PostForm(ModelForm):
    class Meta:
        model = Post
        labels = {'text': 'Текст', 'group': 'Группа'}
        help_texts = {'text': 'Текст поста', 'group': 'Группа, к которой будет относиться пост'}
        fields = ['text', 'group']