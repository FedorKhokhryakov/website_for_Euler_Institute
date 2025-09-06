from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, verbose_name="ФИО")
    laboratory = models.CharField(max_length=100, verbose_name="Лаборатория")
    birth_year = models.IntegerField(verbose_name="Год рождения")
    graduation_year = models.IntegerField(verbose_name="Год окончания вуза")
    academic_degree = models.CharField(max_length=100, blank=True, verbose_name="Ученая степень")
    degree_year = models.IntegerField(null=True, blank=True, verbose_name="Год получения степени")
    status = models.CharField(max_length=100, verbose_name="Статус")
    position = models.CharField(max_length=100, verbose_name="Должность")
    rank = models.CharField(max_length=100, verbose_name="Звание")
    rate = models.CharField(max_length=100, verbose_name="Ставка")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def get_absolute_url(self):
        return reverse('user_publications', kwargs={'user_id': self.user.id})


class Publication(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    results = models.TextField(verbose_name="Результаты", blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('publication_detail', kwargs={'pk': self.pk})