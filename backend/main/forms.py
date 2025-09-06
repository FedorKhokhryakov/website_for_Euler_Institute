from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Publication, UserProfile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Подтверждение пароля'})
    )

    # Поля профиля - все текстовые
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ФИО'})
    )
    laboratory = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Лаборатория'})
    )
    birth_year = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Год рождения'})
    )
    graduation_year = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Год окончания вуза'})
    )
    academic_degree = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ученая степень'})
    )
    degree_year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Год получения степени'})
    )
    status = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Статус'})
    )
    position = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Должность'})
    )
    rank = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Звание'})
    )
    rate = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ставка'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

            # Создаем профиль с данными из формы
            UserProfile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                laboratory=self.cleaned_data['laboratory'],
                birth_year=self.cleaned_data['birth_year'],
                graduation_year=self.cleaned_data['graduation_year'],
                academic_degree=self.cleaned_data['academic_degree'],
                degree_year=self.cleaned_data.get('degree_year'),
                status=self.cleaned_data['status'],
                position=self.cleaned_data['position'],
                rank=self.cleaned_data['rank'],
                rate=self.cleaned_data['rate']
            )

        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'full_name', 'laboratory', 'birth_year', 'graduation_year',
            'academic_degree', 'degree_year', 'status', 'position',
            'rank', 'rate'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'laboratory': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'academic_degree': forms.TextInput(attrs={'class': 'form-control'}),
            'degree_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'rank': forms.TextInput(attrs={'class': 'form-control'}),
            'rate': forms.TextInput(attrs={'class': 'form-control'}),
        }


class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['title', 'content', 'results']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'results': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

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
            ('publications', 'Публикации'),
            ('users', 'Пользователи')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='publications'
    )