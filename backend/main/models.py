from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    first_name_rus = models.CharField('Имя (рус)', max_length=150)
    second_name_rus = models.CharField('Фамилия (рус)', max_length=150)
    middle_name_rus = models.CharField('Отчество (рус)', max_length=150, blank=True)
    first_name_eng = models.CharField('Имя (англ)', max_length=150, blank=True)
    second_name_eng = models.CharField('Фамилия (англ)', max_length=150, blank=True)
    middle_name_eng = models.CharField('Отчество (англ)', max_length=150, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    group = models.CharField('Группа', max_length=10, choices=[('SPbU', 'СПбГУ'), ('POMI', 'ПОМИ')])
    year_of_birth = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1900), MaxValueValidator(2100)])
    year_of_graduation = models.IntegerField(null=True, blank=True)
    academic_degree = models.CharField('Ученая степень', max_length=100, blank=True)
    year_of_degree = models.IntegerField('Год получения степени', null=True, blank=True)
    position = models.CharField('Должность', max_length=100, blank=True)

    def __str__(self):
        return f"{self.second_name_rus} {self.first_name_rus}"


    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Role(models.Model):
    ROLE_CHOICES = [
        ('MasterAdmin', 'Главный администратор'),
        ('AdminSPbU', 'Администратор СПбГУ'),
        ('AdminPOMI', 'Администратор ПОМИ'),
        ('UserSPbU', 'Пользователь СПбГУ'),
        ('UserPOMI', 'Пользователь ПОМИ'),
    ]

    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'role']


class YearReport(models.Model):
    STATUS_CHOICES = [
        ('idle', 'Черновик'),
        ('on_checking', 'На проверке'),
        ('to_rework', 'На доработку'),
        ('signed', 'Подписан'),
    ]

    year = models.IntegerField(validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    report_text = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='idle')
    admin_comment = models.TextField(blank=True)
    #created_at = models.DateTimeField(auto_now_add=True)
    #updated_at = models.DateTimeField(auto_now=True)
    #users = models.ManyToManyField(User, through='UserReport')

class UserReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report = models.ForeignKey(YearReport, on_delete=models.CASCADE)


class Post(models.Model):
    type = models.CharField(max_length=20)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #authors = models.ManyToManyField(User, through='PostAuthor')

class Publication(models.Model):
    class Status(models.TextChoices):
        PREPRINT = "preprint", "Препринт"
        SUBMITTED = "submitted", "Отправлено"
        ACCEPTED = "accepted", "Принято"
        PUBLISHED = "published", "Опубликовано"

    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='publication')
    current_status = models.CharField(max_length=20, choices=Status.choices, default=Status.PREPRINT)

    title = models.CharField(max_length=255)
    language = models.CharField(max_length=50)
    preprint_date = models.DateField()
    preprint_number = models.CharField(max_length=100)
    preprint_document_file_path = models.CharField(max_length=500, blank=True)

    submission_date = models.DateField(null=True, blank=True)
    journal_name = models.CharField(max_length=255, blank=True)
    journal_issn = models.CharField(max_length=20, blank=True)
    submission_document_file_path = models.CharField(max_length=500, blank=True)

    acceptance_date = models.DateField(null=True, blank=True)
    doi = models.CharField(max_length=100, blank=True)
    accepted_document_file_path = models.CharField(max_length=500, blank=True)

    publication_date = models.DateField(null=True, blank=True)
    journal_volume = models.IntegerField(null=True, blank=True)
    journal_number = models.IntegerField(null=True, blank=True)
    journal_pages_or_article_number = models.CharField(max_length=50, blank=True)
    journal_level = models.CharField(max_length=50, blank=True)
    publicated_document_file_path = models.CharField(max_length=500, blank=True)

class ExternalPublicationAuthor(models.Model):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='external_authors')
    author_name = models.CharField(max_length=255)

class Presentation(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='presentation')
    title = models.CharField(max_length=255)
    language = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    presentation_place = models.CharField(max_length=255, blank=True)
    presentation_date = models.DateField(blank=True)


class PostAuthor(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='authors', verbose_name="Публикация")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authors_post', verbose_name="Автор")

    class Meta:
        verbose_name = "Автор публикации"
        verbose_name_plural = "Авторы публикаций"
        unique_together = ['post', 'user']


class Report(models.Model):
    REPORT_TYPES = [
        ('annual_user', 'Годовой отчет пользователя'),
        ('annual_lab', 'Годовой отчет лаборатории'),
        ('custom', 'Произвольный отчет'),
    ]

    REPORT_STATUSES = [
        ('pending', 'В обработке'),
        ('processing', 'Формируется'),
        ('completed', 'Завершен'),
        ('failed', 'Ошибка'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reports',
                                   verbose_name="Создатель отчета", null=True, blank=True)
    year = models.IntegerField(verbose_name="Год отчета")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name="Тип отчета", null=True, blank=True)
    status = models.CharField(max_length=20, choices=REPORT_STATUSES, default='pending', verbose_name="Статус")
    name = models.CharField(max_length=255, verbose_name="Название отчета")
    file_path = models.CharField(max_length=500, blank=True, null=True, verbose_name="Путь к файлу")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        verbose_name = "Отчет"
        verbose_name_plural = "Отчеты"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def get_download_url(self):
        return f"/api/reports/{self.id}/download/"

    def generate_filename(self):
        return f"report_{self.user.username}_{self.year}_{self.created_at.strftime('%Y%m%d_%H%M%S')}.{self.format}"


class ImpersonationSession(models.Model):
    impersonator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='impersonator_sessions')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='target_sessions')
    impersonation_token = models.TextField()
    context_token = models.TextField()
    started_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Сессия имперсонализации"
        verbose_name_plural = "Сессии имперсонализации"