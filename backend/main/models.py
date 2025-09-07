from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class User(AbstractUser):
    # Переопределяем email поле чтобы сделать unique
    email = models.EmailField(_('email address'), unique=True)

    laboratory = models.CharField(max_length=100, blank=True, verbose_name="Лаборатория")
    year_of_birth = models.IntegerField(null=True, blank=True, verbose_name="Год рождения")
    year_of_graduation = models.IntegerField(null=True, blank=True, verbose_name="Год окончания вуза")
    academic_degree = models.CharField(max_length=100, blank=True, verbose_name="Ученая степень")
    year_of_degree = models.IntegerField(null=True, blank=True, verbose_name="Год получения степени")
    status = models.CharField(max_length=100, blank=True, verbose_name="Статус")
    position = models.CharField(max_length=100, blank=True, verbose_name="Должность")
    title = models.CharField(max_length=100, blank=True, verbose_name="Звание")
    fte = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, verbose_name="Ставка")
    is_admin = models.BooleanField(default=False, verbose_name="Администратор")

    # Убираем first_name и last_name из AbstractUser, используем наши
    first_name = None
    last_name = None

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.username} ({self.email})"


class Post(models.Model):
    TYPE_CHOICES = [
        ('article', 'Статья'),
        ('conference', 'Конференция'),
        ('book', 'Книга'),
        ('report', 'Отчет'),
        ('other', 'Другое'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('submitted', 'На рассмотрении'),
        ('accepted', 'Принято'),
        ('published', 'Опубликовано'),
        ('rejected', 'Отклонено'),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Тип публикации")
    tome = models.IntegerField(null=True, blank=True, verbose_name="Том")
    number = models.IntegerField(null=True, blank=True, verbose_name="Номер")
    article_identification_number = models.CharField(max_length=100, blank=True,
                                                     verbose_name="Идентификационный номер статьи")
    pages = models.IntegerField(null=True, blank=True, verbose_name="Страницы")
    year = models.IntegerField(verbose_name="Год публикации")
    language = models.CharField(max_length=50, default='Русский', verbose_name="Язык")
    web_page = models.URLField(blank=True, verbose_name="Веб-страница")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    accepted_at = models.DateTimeField(null=True, blank=True, verbose_name="Принято")

    class Meta:
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()} ({self.year})"

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})


class PostAuthor(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='authors', verbose_name="Публикация")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_authors', verbose_name="Автор")
    order = models.IntegerField(default=0, verbose_name="Порядок автора")

    class Meta:
        verbose_name = "Автор публикации"
        verbose_name_plural = "Авторы публикаций"
        unique_together = ['post', 'user']
        ordering = ['order']

    def __str__(self):
        return f"{self.user.username} - {self.post}"