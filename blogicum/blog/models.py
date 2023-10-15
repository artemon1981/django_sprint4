from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class PublishedModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.')

    class Meta:
        abstract = True


class CreatedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено')

    class Meta:
        abstract = True

class Comment(models.Model):
    text = models.TextField(verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,)
    created_at = models.DateTimeField(auto_now_add=True)
    post_related = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, related_name='comments')

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)


class Category(PublishedModel, CreatedModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, '
        'цифры, дефис и подчёркивание.')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title


class Location(PublishedModel, CreatedModel):
    name = models.CharField(
        max_length=256,
        verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name


class Post(PublishedModel, CreatedModel):
    title = models.CharField(max_length=256,
                             verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем'
                  ' — можно делать отложенные публикации.')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации')
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Местоположение",)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория')
    comment = models.ForeignKey(
        Comment,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Комментарий',)
    image = models.ImageField('Изображение публикации', upload_to='posts_images', blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self) -> str:
        return self.title
