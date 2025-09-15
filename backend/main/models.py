from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.conf import settings


class User(AbstractUser):
    middle_name = models.CharField(_('отчество'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), unique=True)

    laboratory = models.CharField(max_length=100, blank=True, verbose_name="Лаборатория")
    year_of_birth = models.IntegerField(null=True, blank=True, verbose_name="Год рождения")
    year_of_graduation = models.IntegerField(null=True, blank=True, verbose_name="Год окончания вуза")
    academic_degree = models.CharField(max_length=100, blank=True, verbose_name="Ученая степень")
    year_of_degree = models.IntegerField(null=True, blank=True, verbose_name="Год получения степени")
    status = models.CharField(max_length=100, blank=True, verbose_name="Статус")
    position = models.CharField(max_length=100, blank=True, verbose_name="Должность")
    title = models.CharField(max_length=100, blank=True, verbose_name="Звание")
    rate = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, verbose_name="Ставка")
    is_admin = models.BooleanField(default=False, verbose_name="Администратор")


    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        if self.last_name and self.first_name:
            full_name = f"{self.last_name} {self.first_name}"
            if self.middle_name:
                full_name += f" {self.middle_name}"
            return full_name
        return self.username

    @property
    def full_name(self):
        parts = []
        if self.last_name:
            parts.append(self.last_name)
        if self.first_name:
            parts.append(self.first_name)
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts) if parts else self.username


class Post(models.Model):
    TYPE_CHOICES = [
        ('publication', 'Публикация'),
        ('monograph', 'Монография'),
        ('presentation', 'Доклад'),
        ('lecture', 'Курс лекций'),
        ('patent', 'Патент'),
        ('supervision', 'Научное руководство'),
        ('editing', 'Редактирование научных изданий'),
        ('editorial_board', 'Работа в ред. коллегии'),
        ('org_work', 'Научно-организационная работа'),
        ('opposition', 'Оппонирование'),
        ('grant', 'Грант'),
        ('award', 'Награда'),
    ]

    post_type = models.CharField(max_length=50, choices=TYPE_CHOICES, verbose_name="Тип поста")
    priority = models.IntegerField(null=True, blank=True, verbose_name="Приоритет")
    score = models.IntegerField(null=True, blank=True, verbose_name="Балл")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"


class Publication(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="publication")
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=1023, null=True, blank=True)
    journal = models.CharField(max_length=255, null=True, blank=True)
    journal_tome = models.IntegerField(null=True, blank=True)
    journal_number = models.IntegerField(null=True, blank=True)
    article_id = models.CharField(max_length=255, null=True, blank=True)
    pages = models.CharField(max_length=255, null=True, blank=True)
    year = models.PositiveIntegerField()
    language = models.CharField(max_length=255)
    web_page = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    decision_date = models.DateField(null=True, blank=True)
    published_date = models.DateField(null=True, blank=True)
    faculty_coauthors = models.BooleanField(null=True, blank=True)


class Monograph(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="monograph")
    publisher = models.CharField(max_length=255)
    pages = models.PositiveIntegerField()


class Presentation(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="presentation")
    conference = models.CharField(max_length=255)
    city = models.CharField(max_length=255)


class Lecture(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="lecture")
    course_name = models.CharField(max_length=255)
    semester = models.CharField(max_length=50)


class Patent(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="patent")
    number = models.CharField(max_length=50)
    date_registered = models.DateField()


class Supervision(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="supervision")
    student_name = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)


class Editing(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="editing")
    edition_name = models.CharField(max_length=255)


class EditorialBoard(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="editorial_board")
    journal = models.CharField(max_length=255)


class OrgWork(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="org_work")
    organization = models.CharField(max_length=255)


class Opposition(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="opposition")
    thesis_title = models.CharField(max_length=255)


class Grant(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="grant")
    fund_name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)


class Award(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name="award")
    award_name = models.CharField(max_length=255)
    year = models.PositiveIntegerField()


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