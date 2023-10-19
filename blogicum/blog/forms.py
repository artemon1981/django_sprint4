"""Формы проекта."""
from django import forms

from .models import Comment, Post, User


class CommentForm(forms.ModelForm):
    """Форма комментария."""

    class Meta:
        """Мета коммента."""

        model = Comment
        fields = ('text',)


class PostForm(forms.ModelForm):
    """Форма поста."""

    class Meta:
        """Мета поста."""

        model = Post
        fields = ('title', 'text', 'image', 'category', 'pub_date')
        widgets = {'pub_date': forms.DateInput(attrs={'type': 'date'})}


class UserForm(forms.ModelForm):
    """Форма пользователя."""

    class Meta:
        """Мета пользователя."""

        model = User
        fields = ('username', 'email', 'last_name', 'first_name',)
