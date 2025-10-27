import os
from collections import defaultdict

import pypandoc
from datetime import datetime
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import authenticate

from euler import settings
from .models import *
from .utils import *


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


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'first_name_rus', 'second_name_rus', 'middle_name_rus',
            'first_name_eng', 'second_name_eng', 'middle_name_eng',
            'group', 'year_of_birth', 'year_of_graduation',
            'academic_degree', 'year_of_degree', 'position'
        ]

    def validate_group(self, value):
        if value and value not in ['SPbU', 'POMI']:
            raise serializers.ValidationError("Группа должна быть SPbU или POMI")
        return value

    def validate_year_fields(self, value, field_name):
        if value is not None:
            current_year = datetime.now().year
            if value < 1900 or value > current_year + 10:
                raise serializers.ValidationError(f"{field_name} должен быть между 1900 и {current_year + 10}")
        return value


class UserSerializer(BaseUserSerializer):
    pass


class UserInfoSerializer(BaseUserSerializer):
    roles = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ['roles', 'is_admin']
        read_only_fields = ['id']

    def get_roles(self, obj):
        user_roles = obj.roles.all()
        role_objects = [user_role.role for user_role in user_roles]
        return RoleSerializer(role_objects, many=True).data

    def get_is_admin(self, obj):
        return is_admin_user(obj)


class UserCreateSerializer(serializers.ModelSerializer):
    login = serializers.CharField(source='username', required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    roles = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            'login', 'password', 'roles',
            'second_name_rus', 'first_name_rus', 'middle_name_rus',
            'second_name_eng', 'first_name_eng', 'middle_name_eng',
            'email'
        ]
        extra_kwargs = {
            'second_name_rus': {'required': True},
            'first_name_rus': {'required': True},
            'middle_name_rus': {'required': False, 'allow_blank': True},
            'second_name_eng': {'required': False, 'allow_blank': True},
            'first_name_eng': {'required': False, 'allow_blank': True},
            'middle_name_eng': {'required': False, 'allow_blank': True},
            'email': {'required': True, 'allow_blank': True},
        }

    def validate_login(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким логином уже существует")
        return value

    def validate_roles(self, value):
        if not value:
            raise serializers.ValidationError("Список ролей не может быть пустым")

        valid_roles = ['MasterAdmin', 'SPbUAdmin', 'POMIAdmin', 'SPbUUser', 'POMIUser']
        for role in value:
            if role not in valid_roles:
                raise serializers.ValidationError(f"Недопустимая роль: {role}")

        return value

    def create(self, validated_data):
        roles_data = validated_data.pop('roles')
        username = validated_data.pop('username')
        password = validated_data.pop('password')

        if not validated_data.get('first_name_eng') and validated_data.get('first_name_rus'):
            validated_data['first_name_eng'] = self.transliterate(validated_data['first_name_rus'])

        if not validated_data.get('second_name_eng') and validated_data.get('second_name_rus'):
            validated_data['second_name_eng'] = self.transliterate(validated_data['second_name_rus'])

        if not validated_data.get('middle_name_eng') and validated_data.get('middle_name_rus'):
            validated_data['middle_name_eng'] = self.transliterate(validated_data['middle_name_rus'])

        if any(role in ['MasterAdmin', 'SPbUAdmin', 'SPbUUser'] for role in roles_data):
            validated_data['group'] = 'SPbU'
        elif any(role in ['POMIAdmin', 'POMIUser'] for role in roles_data):
            validated_data['group'] = 'POMI'
        else:
            validated_data['group'] = 'SPbU'

        user = User.objects.create_user(
            username=username,
            password=password,
            **validated_data
        )

        for role_name in roles_data:
            role = Role.objects.get(name=role_name)
            UserRole.objects.create(user=user, role=role)

        return user

    def transliterate(self, text):
        translit_dict = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '',
            'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Ъ': '',
            'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
        }

        result = ''
        for char in text:
            result += translit_dict.get(char, char)
        return result


class UserUpdateSerializer(BaseUserSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        validators=[validate_password]
    )

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ['password']
        extra_kwargs = {
            'username': {'required': False},
            'email': {'required': False},
            'first_name_rus': {'required': False},
            'second_name_rus': {'required': False},
        }

    def validate_username(self, value):
        if value and User.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует")
        return value

    def validate_email(self, value):
        if value and User.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def validate_group(self, value):
        if value and value not in ['SPbU', 'POMI']:
            raise serializers.ValidationError("Группа должна быть SPbU или POMI")
        return value

    def validate_year(self, value, field_name):
        if value is not None:
            current_year = datetime.now().year
            if value < 1900 or value > current_year + 10:
                raise serializers.ValidationError(f"{field_name} должен быть между 1900 и {current_year + 10}")
        return value

    def validate_year_of_birth(self, value):
        return self.validate_year(value, "Год рождения")

    def validate_year_of_graduation(self, value):
        return self.validate_year(value, "Год окончания")

    def validate_year_of_degree(self, value):
        return self.validate_year(value, "Год получения степени")

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            if value is not None:
                setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class BasePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'type', 'comment', 'created_at', 'updated_at']


class BaseExternalAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalPublicationAuthor
        fields = ['id', 'author_name']


class BasePostWithDetailsMixin:
    details = serializers.SerializerMethodField()

    def get_details(self, obj):
        if hasattr(obj, 'post') and hasattr(obj.post, 'type'):
            return self.get_specific_details(obj)
        return {}

    def get_specific_details(self, obj):
        raise NotImplementedError("Должен быть реализован в дочернем классе")


class BaseCreateUpdateMixin:
    def handle_external_authors(self, instance, external_authors):
        if external_authors is not None:
            instance.external_authors.all().delete()
            for author_name in external_authors:
                if author_name.strip():
                    ExternalPublicationAuthor.objects.create(
                        publication=instance,
                        author_name=author_name.strip()
                    )


class PostSerializer(BasePostSerializer):
    pass


class PublicationReadSerializer(serializers.ModelSerializer):
    external_authors = BaseExternalAuthorSerializer(many=True, read_only=True)
    external_authors_list = serializers.SerializerMethodField()

    class Meta:
        model = Publication
        fields = [
            'id', 'current_status', 'title', 'language', 'preprint_date',
            'preprint_number', 'preprint_document_file_path', 'submission_date',
            'journal_name', 'journal_issn', 'submission_document_file_path',
            'acceptance_date', 'accepted_document_file_path', 
            'online_first_publication_date', 'doi', 'online_first_document_file_path',
            'publication_date', 'journal_volume', 'journal_number',
            'journal_pages_or_article_number', 'journal_level',
            'publicated_document_file_path', 'external_authors', 'external_authors_list'
        ]

    def get_external_authors_list(self, obj):
        return [author.author_name for author in obj.external_authors.all()]


class PresentationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presentation
        fields = [
            'id', 'title', 'language', 'description',
            'presentation_place', 'presentation_date'
        ]


class PostWithDetailsSerializer(serializers.Serializer):
    post = PostSerializer()
    details = serializers.SerializerMethodField()

    def get_details(self, obj):
        post_instance = obj.get('post')
        if not post_instance:
            return {}

        post_type = post_instance.type

        from .utils import get_post_details
        return get_post_details(post_instance)


class PostCreateSerializer(BasePostSerializer):
    class Meta(BasePostSerializer.Meta):
        fields = ['type', 'comment']


class BaseDetailCreateSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True
        exclude = ['id', 'post']


class PublicationCreateSerializer(BaseDetailCreateSerializer, BaseCreateUpdateMixin):
    external_authors_list = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=[]
    )

    preprint_file = serializers.FileField(required=False, write_only=True, allow_null=True)
    online_first_file = serializers.FileField(required=False, write_only=True, allow_null=True)
    published_file = serializers.FileField(required=False, write_only=True, allow_null=True)

    class Meta(BaseDetailCreateSerializer.Meta):
        model = Publication

    def create(self, validated_data):
        preprint_file = validated_data.pop('preprint_file', None)
        online_first_file = validated_data.pop('online_first_file', None)
        published_file = validated_data.pop('published_file', None)
        external_authors = validated_data.pop('external_authors_list', [])
        publication = super().create(validated_data)

        self.handle_files(publication, {
            'preprint': preprint_file,
            'online_first': online_first_file,
            'published': published_file
        })

        self.handle_external_authors(publication, external_authors)
        return publication

    def update(self, instance, validated_data):
        preprint_file = validated_data.pop('preprint_file', None)
        online_first_file = validated_data.pop('online_first_file', None)
        published_file = validated_data.pop('published_file', None)
        external_authors = validated_data.pop('external_authors_list', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        self.handle_files(instance, {
            'preprint': preprint_file,
            'online_first': online_first_file,
            'published': published_file
        })

        self.handle_external_authors(instance, external_authors)
        return instance

    def handle_files(self, publication, files_dict):
        for file_type, file_obj in files_dict.items():
            if file_obj:
                file_path = get_publication_file_path(publication, file_type, file_obj.name)
                full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
                os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
                
                with open(full_file_path, 'wb+') as destination:
                    for chunk in file_obj.chunks():
                        destination.write(chunk)
                
                file_field = get_file_field_by_type(publication, file_type)
                setattr(publication, file_field, file_path)
        
        publication.save()


class PresentationCreateSerializer(BaseDetailCreateSerializer):
    class Meta(BaseDetailCreateSerializer.Meta):
        model = Presentation


class PostWithDetailsCreateSerializer(serializers.Serializer):
    post = PostCreateSerializer()
    details = serializers.DictField()

    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Пользователь не авторизован")

        post_data = validated_data['post']
        details_data = validated_data['details']
        post_type = post_data['type']

        if request.FILES:
            for file_key in request.FILES:
                if file_key.startswith('preprint_file'):
                    details_data['preprint_file'] = request.FILES[file_key]
                elif file_key.startswith('online_first_file'):
                    details_data['online_first_file'] = request.FILES[file_key]
                elif file_key.startswith('published_file'):
                    details_data['published_file'] = request.FILES[file_key]

        post = Post.objects.create(
            type=post_type,
            comment=post_data.get('comment', '')
        )
        PostAuthor.objects.create(post=post, user=request.user)

        if post_type == 'publication':
            self.create_publication(post, details_data, request.user)
        elif post_type == 'presentation':
            self.create_presentation(post, details_data)
        else:
            post.delete()
            raise serializers.ValidationError(f"Неподдерживаемый тип поста: {post_type}")

        return post

    def create_publication(self, post, details_data, current_user):
        internal_authors = details_data.pop('internal_authors_list', [])
        external_authors = details_data.pop('external_authors_list', [])

        serializer = PublicationCreateSerializer(data=details_data, context=self.context)
        serializer.is_valid(raise_exception=True)
        publication = serializer.save(post=post)

        for user_id in internal_authors:
            if user_id and user_id != current_user.id:
                try:
                    user_obj = User.objects.get(id=user_id)
                    PostAuthor.objects.get_or_create(post=post, user=user_obj)
                except User.DoesNotExist:
                    continue

        for author_name in external_authors:
            ExternalPublicationAuthor.objects.create(
                publication=publication,
                author_name=author_name.strip()
            )

    def create_presentation(self, post, details_data):
        serializer = PresentationCreateSerializer(data=details_data, context=self.context)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post)


class YearReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = YearReport
        fields = ['id', 'year', 'report_text', 'status', 'short_report_text',
            'external_publications', 'admin_comment']

class ScienceReportSubmitSerializer(serializers.Serializer):
    year_report = serializers.CharField(required=True, allow_blank=False)

    def validate_year_report(self, value):
        if not value.strip():
            # raise serializers.ValidationError("Текст отчета не может быть пустым")
            pass
        return value.strip()

class ScienceReportStatusUpdateSerializer(serializers.Serializer):
    new_status = serializers.ChoiceField(choices=['to_rework', 'signed'], required=True)
    admin_comment = serializers.CharField(required=False,  allow_blank=True, default='')

    def validate_new_status(self, value):
        if value not in ['to_rework', 'signed']:
            raise serializers.ValidationError("Недопустимый статус")
        return value

    def validate_admin_comment(self, value):
        if value and len(value.strip()) > 1000:
            raise serializers.ValidationError("Комментарий слишком длинный (максимум 1000 символов)")
        return value.strip()


class ImpersonationStartSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)

    def validate_user_id(self, value):
        try:
            user = User.objects.get(id=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("Целевой пользователь не найден")

class ImpersonationStopSerializer(serializers.Serializer):
    context_token = serializers.CharField(required=True)


class ImpersonationStatusSerializer(serializers.Serializer):
    is_impersonating = serializers.BooleanField()
    impersonator = serializers.DictField(required=False)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    group = serializers.ChoiceField(choices=[('SPbU', 'СПбГУ'), ('POMI', 'ПОМИ')], required=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'group',
            'first_name_rus', 'second_name_rus', 'middle_name_rus',
            'first_name_eng', 'second_name_eng', 'middle_name_eng',
            'year_of_birth', 'year_of_graduation',
            'academic_degree', 'year_of_degree', 'position'
        ]
        extra_kwargs = {
            'first_name_rus': {'required': True},
            'second_name_rus': {'required': True},
            'middle_name_rus': {'required': False, 'allow_blank': True},
            'email': {'required': True},
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
            first_name_rus=validated_data['first_name_rus'],
            second_name_rus=validated_data['second_name_rus'],
            middle_name_rus=validated_data.get('middle_name_rus', ''),
            first_name_eng=validated_data.get('first_name_eng', ''),
            second_name_eng=validated_data.get('second_name_eng', ''),
            middle_name_eng=validated_data.get('middle_name_eng', ''),
            group=validated_data['group'],
            year_of_birth=validated_data.get('year_of_birth'),
            year_of_graduation=validated_data.get('year_of_graduation'),
            academic_degree=validated_data.get('academic_degree', ''),
            year_of_degree=validated_data.get('year_of_degree'),
            position=validated_data.get('position', ''),
        )
        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

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
    type = serializers.ChoiceField(choices=Report.REPORT_TYPES, source='report_type')

    class Meta:
        model = Report
        fields = ['user_id', 'year', 'type']

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

class ReportSaveSerializer(serializers.Serializer):
    external_publications = serializers.CharField(required=False, allow_blank=True, default='')
    short_report_text = serializers.CharField(required=False, allow_blank=True, default='')
    report_text = serializers.CharField(required=True, allow_blank=False)

    def validate_report_text(self, value):
        if not value.strip():
            raise serializers.ValidationError("Текст отчета не может быть пустым")
        return value.strip()

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
    file_type = serializers.ChoiceField(
        choices=['preprint', 'online_first', 'published'],
        required=True
    )

class FileResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    file_path = serializers.CharField(required=False)
    file_type = serializers.CharField()