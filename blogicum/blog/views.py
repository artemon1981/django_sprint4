"""Вью приложения Blog."""
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.views.generic import (CreateView,
                                  DeleteView,
                                  DetailView,
                                  ListView,
                                  UpdateView,
                                  )

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post, User

NUM_POST_ON_PAGE = 10


class PostMixin:
    """Mixin for Post."""

    form_class = PostForm
    template_name = 'blog/create.html'


class CommentMixin:
    """Mixin for Comment."""

    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm


class IndexListView(ListView):
    """Главная страница."""

    model = Post
    template_name = 'blog/index.html'

    ordering = ('-pub_date',)
    queryset = Post.objects.select_related('category',
                                           'location',
                                           'author').filter(
        is_published=True,
        category__is_published=True,
        pub_date__lt=datetime.now()
    ).annotate(comment_count=Count('comments'))
    paginate_by = NUM_POST_ON_PAGE


class PostDetailView(DetailView):
    """Страница выбранной публикации."""

    model = Post
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        """Переопределение dispatch."""
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if (not instance.is_published
            or not instance.category.is_published
            or instance.pub_date > timezone.now()) \
                and instance.author != request.user:
            raise Http404()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Переопределение context."""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related(
                'author'
            )
        )
        return context


class CategoryPostsListView(ListView):
    """Список постов категории."""

    model = Category
    template_name = 'blog/category.html'

    def get_context_data(self, **kwargs):
        """Переопределение context."""
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(Category,
                                     slug=self.kwargs['category_slug'],
                                     is_published=True)
        context['category'] = category
        page_obj = Post.objects.select_related('category',
                                               'location',
                                               'author').filter(
            category__slug=self.kwargs['category_slug'],
            is_published=True, pub_date__lt=datetime.now()).annotate(
             comment_count=Count('comments')).order_by(
            '-pub_date')
        context['page_obj'] = Paginator(page_obj,
                                        NUM_POST_ON_PAGE
                                        ).get_page(
                                         self.request.GET.get('page'))
        return context


class ProfileListView(ListView):
    """Страница профиля пользователя."""

    model = Post
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    paginate_by = NUM_POST_ON_PAGE
    user = None

    def get_queryset(self):
        """Поучение queryset."""
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.select_related('category',
                                           'location',
                                           'author').filter(
            author=self.user).order_by(
            '-pub_date').annotate(comment_count=Count('comments'))

    def get_context_data(self, **kwargs):
        """Переопределение context."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Страница редактирования профиля пользователя."""

    model = User
    template_name = 'blog/user.html'
    form_class = UserForm

    def get_object(self, queryset=None):
        """Получение объекта."""
        return self.request.user

    def get_success_url(self):
        """Удачное перенаправление."""
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user})


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    """Создание публикации."""

    def form_valid(self, form):
        """Валидация формы."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Удачное перенаправление."""
        return reverse('blog:profile', kwargs={'username': self.object.author})


class PostUpdateView(PostMixin, LoginRequiredMixin, UpdateView):
    """Редактирование публикации."""

    model = Post

    def dispatch(self, request, *args, **kwargs):
        """Переопределение dispatch."""
        self.post_obj = get_object_or_404(Post, pk=kwargs['pk'])
        if self.post_obj.author != self.request.user:
            return redirect('blog:post_detail', pk=self.post_obj.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Валидация формы."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Удачное перенаправление."""
        return reverse('blog:post_detail', kwargs={'pk': self.post_obj.pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление публикации."""

    model = Post
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        """Переопределение dispatch."""
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Удачное перенаправление."""
        return reverse('blog:profile', args=[self.request.user])


class CommentCreateView(CommentMixin, LoginRequiredMixin, CreateView):
    """Создание комментария к посту."""

    def dispatch(self, request, *args, **kwargs):
        """Переопределение dispatch."""
        self.post_obj = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Валидация формы."""
        form.instance.post = self.post_obj
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Удачное перенаправление."""
        return reverse('blog:post_detail', kwargs={'pk': self.post_obj.pk})


class CommentUpdateView(CommentMixin, LoginRequiredMixin, UpdateView):
    """Редактирование комментария к посту."""

    pk_url_kwarg = 'comment_pk'

    def dispatch(self, request, *args, **kwargs):
        """Переопределение dispatch."""
        instance = get_object_or_404(Comment, pk=kwargs['comment_pk'])
        if instance.author != request.user:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Удачное перенаправление."""
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление комментария."""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_pk'

    def dispatch(self, request, *args, **kwargs):
        """Переопределение dispatch."""
        instance = get_object_or_404(Comment, pk=kwargs['comment_pk'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        """Удачное перенаправление."""
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})
