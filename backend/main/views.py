from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegistrationForm, PublicationForm, UserProfileForm, SearchForm
from .models import Publication, UserProfile


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = RegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def home(request):
    # Показываем последние публикации на главной
    latest_publications = Publication.objects.all().order_by('-created_at')[:5]
    return render(request, 'main/home.html', {
        'latest_publications': latest_publications
    })


@login_required
def profile(request):
    # Получаем профиль или создаем пустой, если его нет
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # Создаем пустой профиль, если его нет
        profile = UserProfile.objects.create(
            user=request.user,
            full_name=request.user.username,
            laboratory="",
            birth_year=0,
            graduation_year=0,
            academic_degree="",
            status="",
            position="",
            rank="",
            rate=""
        )

    publications = Publication.objects.filter(author=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'main/profile.html', {
        'user': request.user,
        'profile': profile,
        'publications': publications,
        'form': form
    })


@login_required
def add_publication(request):
    if request.method == 'POST':
        form = PublicationForm(request.POST)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.author = request.user
            publication.save()
            messages.success(request, 'Публикация успешно добавлена!')
            return redirect('profile')
    else:
        form = PublicationForm()
    return render(request, 'main/add_publication.html', {'form': form})


@login_required
def all_publications(request):
    publications = Publication.objects.all().order_by('-created_at')
    form = SearchForm(request.GET or None)

    query = request.GET.get('query')
    if query:
        publications = publications.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(results__icontains=query) |
            Q(author__username__icontains=query) |
            Q(author__userprofile__full_name__icontains=query)
        )

    return render(request, 'main/all_publications.html', {
        'publications': publications,
        'form': form,
        'query': query
    })


@login_required
def publication_detail(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    return render(request, 'main/publication_detail.html', {
        'publication': publication
    })


@login_required
def user_publications(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    publications = Publication.objects.filter(author=user).order_by('-created_at')
    return render(request, 'main/user_publications.html', {
        'user': user,
        'publications': publications
    })


@login_required
def search(request):
    form = SearchForm(request.GET or None)
    results = {}
    query = request.GET.get('query', '')
    search_type = request.GET.get('search_type', 'publications')

    if query:
        if search_type == 'publications':
            results['publications'] = Publication.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(results__icontains=query) |
                Q(author__username__icontains=query) |
                Q(author__userprofile__full_name__icontains=query)
            ).order_by('-created_at')
        else:
            results['users'] = User.objects.filter(
                Q(username__icontains=query) |
                Q(userprofile__full_name__icontains=query) |
                Q(userprofile__laboratory__icontains=query) |
                Q(userprofile__position__icontains=query)
            ).distinct()

    return render(request, 'main/search.html', {
        'form': form,
        'results': results,
        'query': query,
        'search_type': search_type
    })


@login_required
def all_users(request):
    users = User.objects.all().order_by('username')
    query = request.GET.get('query')

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(userprofile__full_name__icontains=query) |
            Q(userprofile__laboratory__icontains=query)
        )

    return render(request, 'main/all_users.html', {
        'users': users,
        'query': query
    })