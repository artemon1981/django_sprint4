from datetime import datetime

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.urls import reverse_lazy, reverse

from .forms import CommentForm
from .models import Post, Category, User, Comment
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

NUM_POST_ON_PAGE = 5


class IndexListView(ListView):
    '''Главная страница.'''
    model = Post
    template_name = 'blog/index.html'

    ordering = 'id'
    queryset = Post.objects.select_related('category', 'location', 'author').filter(
        is_published=True,
        category__is_published=True,
        pub_date__lt=datetime.now()
    ).annotate(comment_count=Count('comments'))
    paginate_by = NUM_POST_ON_PAGE




class PostDetailView(DetailView):
    '''Страница выбранной публикации.'''

    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related(
                'author'
            )
        )
        return context


class CategoryPostsListView(ListView):
    '''Список постов категории'''
    model = Category
    template_name = 'blog/category.html'
    ordering = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(Category, slug=self.kwargs['category_slug'], is_published=True)
        context['category'] = category
        page_obj = get_list_or_404(
            Post.objects.select_related('category', 'location', 'author').filter(
                category__slug=self.kwargs['category_slug'],
                is_published=True, pub_date__lt=datetime.now()).annotate(comment_count=Count('comments')))
        context['page_obj'] = Paginator(page_obj, NUM_POST_ON_PAGE).get_page(self.request.GET.get('page'))
        return context


class ProfileListView(ListView, LoginRequiredMixin):
    '''Страница профиля пользователя.'''
    model = Post
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'username'
    paginate_by = NUM_POST_ON_PAGE

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.select_related('category', 'location', 'author').filter(author=self.author).order_by(
            '-pub_date').annotate(comment_count=Count('comments'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class ProfileUpdateView(UpdateView):
    '''Страница редактирования профиля пользователя.'''
    model = User
    template_name = 'blog/user.html'
    form_class = UserChangeForm
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user


class PostCreateView(CreateView):
    '''Создание публикации.'''
    model = Post
    fields = ('title', 'text', 'image', 'category', 'pub_date')
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user])


class PostUpdateView(UpdateView):
    '''Редактирование публикации.'''
    model = Post
    fields = ('title', 'text', 'image', 'category', 'pub_date')
    template_name = 'blog/create.html'
    slug_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['pk']])


class PostDeleteView(DeleteView):
    pass


class CommentCreateView(CreateView):
    '''Создание комментария к посту'''
    model = Comment
    template_name = 'blog/detail.html'
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.post_related = self.post_obj
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_obj.pk})


class CommentUpdateView(UpdateView):
    '''Редактирование комментария к посту'''
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm
    pk_url_kwarg = 'comment_pk'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


    def get_success_url(self):
        return reverse('blog:index')
        # return reverse('blog:post_detail', kwargs={'pk': self.kwargs['post_id']})



class CommentDeleteView(DeleteView):
    pass
