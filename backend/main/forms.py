from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post, PostAuthor, Publication, Monograph, Lecture, Patent, Supervision, Editing, \
    EditorialBoard, OrgWork, Opposition, Grant, Award


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
        required=True,
        label="Авторы"
    )

    journal = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    year = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    publisher = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    pages = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    course_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    semester = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Post
        fields = ['title', 'type', 'authors']

    def save(self, commit=True):
        post = super().save(commit=False)
        if commit:
            post.save()
            self.save_authors(post)
            self.save_child(post)  # <-- добавляем дочерний объект
        return post

    def save_authors(self, post):
        PostAuthor.objects.filter(post=post).delete()
        for order, author in enumerate(self.cleaned_data['authors']):
            PostAuthor.objects.create(post=post, user=author, order=order)

    def save_child(self, post):
        """Создаём дочерний объект в зависимости от типа поста"""
        if post.type == 'publication':
            Publication.objects.get_or_create(
                post=post,
                defaults={
                    'journal': self.cleaned_data.get('journal', ''),
                    'year': self.cleaned_data.get('year', 2000)
                }
            )
        elif post.type == 'monograph':
            Monograph.objects.get_or_create(
                post=post,
                defaults={
                    'publisher': self.cleaned_data.get('publisher', ''),
                    'pages': self.cleaned_data.get('pages', 1)
                }
            )
        elif post.type == 'lectures':
            Lecture.objects.get_or_create(
                post=post,
                defaults={
                    'course_name': self.cleaned_data.get('course_name', ''),
                    'semester': self.cleaned_data.get('semester', '')
                }
            )
        elif post.type == 'patents':
            Patent.objects.get_or_create(
                post=post,
                defaults={
                    'number': self.cleaned_data.get('number', ''),
                    'date_registered': self.cleaned_data.get('date_registered', None)
                }
            )
        elif post.type == 'supervision':
            Supervision.objects.get_or_create(
                post=post,
                defaults={
                    'student_name': self.cleaned_data.get('student_name', ''),
                    'topic': self.cleaned_data.get('topic', '')
                }
            )
        elif post.type == 'editing':
            Editing.objects.get_or_create(
                post=post,
                defaults={
                    'edition_name': self.cleaned_data.get('edition_name', '')
                }
            )
        elif post.type == 'editorial_board':
            EditorialBoard.objects.get_or_create(
                post=post,
                defaults={
                    'journal': self.cleaned_data.get('journal', '')
                }
            )
        elif post.type == 'org_work':
            OrgWork.objects.get_or_create(
                post=post,
                defaults={
                    'organization': self.cleaned_data.get('organization', '')
                }
            )
        elif post.type == 'opposition':
            Opposition.objects.get_or_create(
                post=post,
                defaults={
                    'thesis_title': self.cleaned_data.get('thesis_title', '')
                }
            )
        elif post.type == 'grants':
            Grant.objects.get_or_create(
                post=post,
                defaults={
                    'fund_name': self.cleaned_data.get('fund_name', ''),
                    'amount': self.cleaned_data.get('amount', 0)
                }
            )
        elif post.type == 'awards':
            Award.objects.get_or_create(
                post=post,
                defaults={
                    'award_name': self.cleaned_data.get('award_name', ''),
                    'year': self.cleaned_data.get('year', 2000)
                }
            )


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
    TYPE_CHOICES = [('', 'Все типы')] + [(t[0], t[1]) for t in Post.TYPE_CHOICES]

    YEAR_CHOICES = [('', 'Все годы')] + [(year, str(year)) for year in range(2000, 2031)]

    type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Тип публикации"
    )

    year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Год публикации"
    )

    laboratory = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Фильтр по лаборатории автора...'
        }),
        label="Лаборатория"
    )



class QuickPostEditForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Название',
            'type': 'Тип публикации',
        }