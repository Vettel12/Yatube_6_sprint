from django.db import models
from django.forms import ModelForm
from django import forms

from .models import Post, Comment

class PostForm(ModelForm):
    class Meta:
        model = Post
        labels = {'text': 'Текст', 'group': 'Группа'}
        help_texts = {'text': 'Текст поста', 'group': 'Группа, к которой будет относиться пост'}
        fields = ['group', 'text', 'image']

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': 'Добавить комментарий'}
        help_texts = {'text': 'Текст комментария'}
        widgets = {
            'text': forms.Textarea(attrs={'cols': 80, 'rows': 5})  # Определение виджета <textarea>
        }