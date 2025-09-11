from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post, PostAuthor


class CustomUserCreationForm(UserCreationForm):

    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Фамилия'})
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя'})
    )
    middle_name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Отчество'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтверждение пароля'})
    )

    laboratory = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Лаборатория'})
    )
    year_of_birth = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Год рождения'})
    )
    year_of_graduation = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Год окончания вуза'})
    )
    academic_degree = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ученая степень'})
    )
    year_of_degree = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Год получения степени'})
    )
    status = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Статус'})
    )
    position = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Должность'})
    )
    title = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Звание'})
    )
    fte = forms.DecimalField(
        required=False,
        max_digits=3,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ставка (0.0-1.0)',
            'step': '0.01',
            'min': '0',
            'max': '1'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2',
                  'last_name', 'first_name', 'middle_name',
                  'laboratory', 'year_of_birth', 'year_of_graduation',
                  'academic_degree', 'year_of_degree', 'status',
                  'position', 'title', 'fte']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.last_name = self.cleaned_data['last_name']
        user.first_name = self.cleaned_data['first_name']
        user.middle_name = self.cleaned_data['middle_name']

        user.laboratory = self.cleaned_data['laboratory']
        user.year_of_birth = self.cleaned_data['year_of_birth']
        user.year_of_graduation = self.cleaned_data['year_of_graduation']
        user.academic_degree = self.cleaned_data['academic_degree']
        user.year_of_degree = self.cleaned_data.get('year_of_degree')
        user.status = self.cleaned_data['status']
        user.position = self.cleaned_data['position']
        user.title = self.cleaned_data['title']
        user.fte = self.cleaned_data['fte']

        if commit:
            user.save()

        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username', 'email',
            'last_name', 'first_name', 'middle_name',
            'laboratory', 'year_of_birth', 'year_of_graduation',
            'academic_degree', 'year_of_degree', 'status',
            'position', 'title', 'fte'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'laboratory': forms.TextInput(attrs={'class': 'form-control'}),
            'year_of_birth': forms.NumberInput(attrs={'class': 'form-control'}),
            'year_of_graduation': forms.NumberInput(attrs={'class': 'form-control'}),
            'academic_degree': forms.TextInput(attrs={'class': 'form-control'}),
            'year_of_degree': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'fte': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '1'
            }),
        }


class PostForm(forms.ModelForm):
    authors = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Post
        fields = [
            'type', 'tome', 'number', 'article_identification_number',
            'pages', 'year', 'language', 'web_page', 'comment', 'authors'
        ]
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'tome': forms.NumberInput(attrs={'class': 'form-control'}),
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'article_identification_number': forms.TextInput(attrs={'class': 'form-control'}),
            'pages': forms.NumberInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'language': forms.TextInput(attrs={'class': 'form-control'}),
            'web_page': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'comment': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Комментарии к публикации...'}),
        }

        labels = {
            'type': 'Тип публикации',
            'tome': 'Том',
            'number': 'Номер',
            'article_identification_number': 'Идентификационный номер статьи',
            'pages': 'Количество страниц',
            'year': 'Год публикации',
            'language': 'Язык',
            'web_page': 'Веб-страница',
            'comment': 'Комментарий',
            'authors': 'Авторы',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['language'].initial = 'Русский'

    def save(self, commit=True):
        post = super().save(commit=False)

        if commit:
            post.save()
            self.save_authors(post)

        return post

    def save_authors(self, post):
        PostAuthor.objects.filter(post=post).delete()

        authors = self.cleaned_data['authors']
        for order, author in enumerate(authors):
            PostAuthor.objects.create(post=post, user=author, order=order)


class SearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Поиск по публикациям и пользователям...'
        })
    )
    search_type = forms.ChoiceField(
        choices=[
            ('posts', 'Публикации'),
            ('users', 'Пользователи')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='posts'
    )


class PostFilterForm(forms.Form):
    TYPE_CHOICES = [
        ('', 'Все типы'),
        ('article', 'Статья'),
        ('conference', 'Конференция'),
        ('book', 'Книга'),
        ('report', 'Отчет'),
        ('other', 'Другое'),
    ]

    YEAR_CHOICES = [('', 'Все годы')] + [(year, str(year)) for year in range(2020, 2031)]

    type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    laboratory = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Фильтр по лаборатории...'
        })
    )



class QuickPostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['status', 'comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }