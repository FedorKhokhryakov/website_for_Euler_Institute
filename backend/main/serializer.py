import os
from collections import defaultdict

import pypandoc
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.contrib.auth import authenticate

from euler import settings
from .models import *

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

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'middle_name',
            'is_admin', 'laboratory', 'year_of_birth', 'year_of_graduation', 'year_of_degree',
            'title', 'position', 'rate', 'status',
        ]
        read_only_fields = ['id']

class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

class BasePostSerializer(serializers.ModelSerializer):
    post = PostSerializer()
    details = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def get_details(self, obj):
        data = {}
        for field in self.Meta.model._meta.fields:
            if field.name != 'post':
                data[field.name] = getattr(obj, field.name)
        return data


    def to_internal_value(self, data):
        # Перемещаем поля из details на верхний уровень
        details_data = data.pop('details', {})
        data.update(details_data)
        return super().to_internal_value(data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        details = {}
        for key, value in representation.items():
            if key not in ['post']:
                details[key] = value
        return {
            'post': representation.get('post', {}),
            'details': details
        }

    def create(self, validated_data):
        post_data = validated_data.pop('post')
        details_data = validated_data

        post_serializer = PostSerializer(data=post_data)
        post_serializer.is_valid(raise_exception=True)
        post = post_serializer.save()

        instance = self.Meta.model.objects.create(post=post, **details_data)

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            PostAuthor.objects.create(post=post, user=request.user)
        
        return instance

    def update(self, instance, validated_data):
        post_data = validated_data.pop('post', None)
        if post_data:
            post_serializer = PostSerializer(instance.post, data=post_data, partial=True)
            post_serializer.is_valid(raise_exception=True)
            post_serializer.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class PublicationSerializer(BasePostSerializer):
    class Meta:
        model = Publication
        fields = '__all__'


class MonographSerializer(BasePostSerializer):
    class Meta:
        model = Monograph
        fields = '__all__'

class PresentationSerializer(BasePostSerializer):
    class Meta:
        model = Presentation
        fields = '__all__'

class LectureSerializer(BasePostSerializer):
    class Meta:
        model = Lecture
        fields = '__all__'


class PatentSerializer(BasePostSerializer):
    class Meta:
        model = Patent
        fields = '__all__'


class SupervisionSerializer(BasePostSerializer):
    class Meta:
        model = Supervision
        fields = '__all__'


class EditingSerializer(BasePostSerializer):
    class Meta:
        model = Editing
        fields = '__all__'


class EditorialBoardSerializer(BasePostSerializer):
    class Meta:
        model = EditorialBoard
        fields = '__all__'


class OrgWorkSerializer(BasePostSerializer):
    class Meta:
        model = OrgWork
        fields = '__all__'


class OppositionSerializer(BasePostSerializer):
    class Meta:
        model = Opposition
        fields = '__all__'


class GrantSerializer(BasePostSerializer):
    class Meta:
        model = Grant
        fields = '__all__'


class AwardSerializer(BasePostSerializer):
    class Meta:
        model = Award
        fields = '__all__'


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
