from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Post, PostAuthor


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
        return 'admin' if obj.is_staff or obj.is_superuser else 'user'


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
            'article': 'Научный журнал',
            'conference': 'Материалы конференции',
            'book': 'Издательство',
            'report': 'Отчет',
            'other': 'Публикация'
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