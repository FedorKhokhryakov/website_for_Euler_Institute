import os
from collections import defaultdict

import pypandoc
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import authenticate

from euler import settings
from .models import User, Post, PostAuthor, Report


class UserAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                 'is_admin', 'laboratory', 'position',]
        read_only_fields = ['id', 'is_admin']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                    return data
                else:
                    raise serializers.ValidationError('User account is disabled.')
            else:
                raise serializers.ValidationError('Invalid username or password.')
        else:
            raise serializers.ValidationError('Must include username and password.')


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    birth_year = serializers.IntegerField(source='year_of_birth')
    graduation_year = serializers.IntegerField(source='year_of_graduation')
    degree_year = serializers.IntegerField(source='year_of_degree')
    academic_title = serializers.CharField(source='title')
    rate = serializers.DecimalField(source='fte', max_digits=3, decimal_places=2)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'middle_name',
            'role', 'laboratory', 'birth_year', 'graduation_year', 'academic_degree',
            'degree_year', 'academic_title', 'position', 'rate', 'status',
        ]
        read_only_fields = ['id']

    def get_role(self, obj):
        return 'admin' if obj.is_admin else 'user'


class PublicationSerializer(serializers.ModelSerializer):
    authors = serializers.SerializerMethodField()
    authorCount = serializers.SerializerMethodField()

    title = serializers.SerializerMethodField()
    receivedDate = serializers.SerializerMethodField()
    decisionDate = serializers.SerializerMethodField()
    publishedDate = serializers.SerializerMethodField()
    journal = serializers.SerializerMethodField()
    volume = serializers.CharField(source='tome')
    issue = serializers.CharField(source='number')
    articleId = serializers.CharField(source='article_identification_number')
    userId = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at')
    updatedAt = serializers.DateTimeField(source='accepted_at')
    facultyCoauthors = serializers.SerializerMethodField()
    webpage = serializers.URLField(source='web_page')

    class Meta:
        model = Post
        fields = [
            'id', 'type', 'title', 'authors', 'authorCount', 'receivedDate',
            'decisionDate', 'publishedDate', 'journal', 'volume', 'issue',
            'articleId', 'pages', 'year', 'language', 'webpage', 'facultyCoauthors',
            'comment', 'userId', 'createdAt', 'updatedAt', 'status'
        ]

    def get_authors(self, obj):
        authors = obj.authors.select_related('user').order_by('order')
        return [
            f"{author.user.last_name} {author.user.first_name} {author.user.middle_name or ''}".strip()
            for author in authors
        ]

    def get_authorCount(self, obj):
        return obj.authors.count()

    def get_title(self, obj):
        return f"{obj.get_type_display()} {obj.year}"

    def get_receivedDate(self, obj):
        return obj.created_at.date() if obj.created_at else None

    def get_decisionDate(self, obj):
        return obj.accepted_at.date() if obj.accepted_at else None

    def get_publishedDate(self, obj):
        if obj.year:
            return f"{obj.year}-01-01"
        return None

    def get_journal(self, obj):
        type_mapping = {
            'publication': 'Публикация',
            'monograph': 'Монография',
            'reports': 'Доклад',
            'lectures': 'Курс лекций',
            'patents': 'Патент',
            'supervision': 'Научное руководство',
            'editing': 'Редактирование научных изданий',
            'editorial_board': 'Работа в ред. коллегии',
            'org_work': 'Научно-организационная работа',
            'opposition': 'Оппонирование',
            'grants': 'Грант',
            'awards': 'Награда'
        }
        return type_mapping.get(obj.type, 'Публикация')

    def get_facultyCoauthors(self, obj):
        return obj.authors.count() > 1

    def get_userId(self, obj):
        first_author = obj.authors.select_related('user').first()
        print(first_author)
        return first_author.user.id if first_author else None


class PublicationCreateSerializer(serializers.ModelSerializer):
    authors = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True
    )

    title = serializers.CharField(write_only=True, required=False)
    receivedDate = serializers.DateField(write_only=True, required=False, source='received_date')
    decisionDate = serializers.DateField(write_only=True, required=False, source='decision_date')
    publishedDate = serializers.DateField(write_only=True, required=False, source='published_date')
    journal = serializers.CharField(write_only=True, required=False, source='journal_name')
    volume = serializers.CharField(write_only=True, required=False, source='tome')
    issue = serializers.CharField(write_only=True, required=False, source='number')
    articleId = serializers.CharField(write_only=True, required=False, source='article_identification_number')
    webpage = serializers.URLField(write_only=True, required=False, source='web_page')
    facultyCoauthors = serializers.BooleanField(write_only=True, required=False, source='has_faculty_coauthors')

    class Meta:
        model = Post
        fields = [
            'type', 'title', 'authors', 'receivedDate', 'decisionDate', 'publishedDate',
            'journal', 'volume', 'issue', 'articleId', 'pages', 'year', 'language',
            'webpage', 'facultyCoauthors', 'comment'
        ]

    def create(self, validated_data):
        volume = validated_data.pop('tome', None)
        if volume and volume != 'string':
            try:
                validated_data['tome'] = int(volume)
            except (ValueError, TypeError):
                validated_data['tome'] = None
        else:
            validated_data['tome'] = None


        issue = validated_data.pop('number', None)
        if issue and issue != 'string':
            try:
                validated_data['number'] = int(issue)
            except (ValueError, TypeError):
                validated_data['number'] = None
        else:
            validated_data['number'] = None

        pges = validated_data.pop('pages', None)
        if pges and pges != 'string':
            try:
                validated_data['number'] = int(pges)
            except (ValueError, TypeError):
                validated_data['number'] = None
        else:
            validated_data['number'] = None

        authors_ids = validated_data.pop('authors')
        post = Post.objects.create(**validated_data)

        for order, author_id in enumerate(authors_ids):
            try:
                author = User.objects.get(id=author_id)
                PostAuthor.objects.create(post=post, user=author, order=order)
            except User.DoesNotExist:
                continue

        return post


class OwnerCheckSerializer(serializers.Serializer):
    isOwner = serializers.BooleanField()
    isAdmin = serializers.BooleanField()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password',
            'first_name', 'last_name', 'middle_name'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'middle_name': {'required': False, 'allow_blank': True}
        }

    def validate(self, attrs):
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "Пользователь с таким именем уже существует"})

        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Пользователь с таким email уже зарегистрирован"})

        return attrs


    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            middle_name=validated_data.get('middle_name', '')
        )
        return user


class UserListSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    department = serializers.CharField(source='laboratory', allow_null=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'middle_name',
            'department', 'role'
        ]

    def get_role(self, obj):
        return 'admin' if obj.is_admin else 'user'

class ReportSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ')

    class Meta:
        model = Report
        fields = ['id', 'name', 'created_at', 'status', 'download_url']

    def get_download_url(self, obj):
        return obj.get_download_url()


class ReportCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    year = serializers.IntegerField()
    format = serializers.ChoiceField(choices=Report.REPORT_FORMATS)
    type = serializers.ChoiceField(choices=Report.REPORT_TYPES, source='report_type')

    class Meta:
        model = Report
        fields = ['user_id', 'year', 'format', 'type']

    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")

    def create(self, validated_data):
        user = validated_data.pop('user_id')
        request = self.context.get('request')

        report = Report.objects.create(
            user=user,
            created_by=request.user,
            name=f"Отчет по {user.last_name} {user.first_name[0]}.{user.middle_name[0] if user.middle_name else ''} за {validated_data['year']} г.",
            **validated_data
        )

        self.generate_report_async(report)

        return report

    def generate_report_async(self, report):

        try:
            report.status = 'processing'
            report.save()

            self.generate_report_content(report)

            report.status = 'completed'
            report.save()

        except Exception as e:
            report.status = 'failed'
            report.save()
            print(f"Ошибка генерации отчета {report.id}: {str(e)}")

    def generate_report_content(self, report):
        posts = Post.objects.filter(authors__user=report.user, year=report.year).order_by("type", "year")

        grouped = defaultdict(list)
        for post in posts:
            grouped[post.get_type_display()].append(post)

        report_text = f"# Отчёт по публикациям пользователя {report.user.username} за {report.year} год\n\n"
        for type_name, items in grouped.items():
            report_text += f"## {type_name}\n"
            for p in items:
                report_text += f"- {p.year}: {p.article_identification_number or 'Без номера'}"
                if p.web_page:
                    report_text += f" ([ссылка]({p.web_page}))"
                report_text += "\n"
            report_text += "\n"

        reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
        os.makedirs(reports_dir, exist_ok=True)

        filename = report.generate_filename()
        report.file_path = os.path.join(reports_dir, filename)

        try:
            if report.format == 'rtf':
                pypandoc.convert_text(report_text, "rtf", format="md", outputfile=report.file_path,
                                      extra_args=["--standalone"])
            elif report.format == 'pdf':
                pypandoc.convert_text(report_text, "pdf", format="md", outputfile=report.file_path,
                                      extra_args=["--standalone"])
            elif report.format == 'docx':
                pypandoc.convert_text(report_text, "docx", format="md", outputfile=report.file_path,
                                      extra_args=["--standalone"])

        except Exception as e:
            raise Exception(f"Ошибка конвертации отчета: {str(e)}")
