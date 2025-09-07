from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, UserProfileForm, PostForm, SearchForm
from .models import User, Post, PostAuthor


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def home(request):
    latest_posts = Post.objects.all().order_by('-created_at')[:5]
    return render(request, 'main/home.html', {
        'latest_posts': latest_posts
    })


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    user_posts = Post.objects.filter(authors__user=request.user).distinct()

    return render(request, 'main/profile.html', {
        'form': form,
        'posts': user_posts
    })


@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()

            authors = form.cleaned_data['authors']
            if request.user not in authors:
                max_order = PostAuthor.objects.filter(post=post).aggregate(models.Max('order'))['order__max'] or 0
                PostAuthor.objects.create(post=post, user=request.user, order=max_order + 1)

            messages.success(request, 'Публикация успешно добавлена!')
            return redirect('profile')
    else:
        form = PostForm(initial={'authors': [request.user]})

    return render(request, 'main/add_post.html', {'form': form})


@login_required
def all_posts(request):
    posts = Post.objects.all().order_by('-created_at')
    form = SearchForm(request.GET or None)

    query = request.GET.get('query')
    if query:
        posts = posts.filter(
            Q(article_identification_number__icontains=query) |
            Q(comment__icontains=query) |
            Q(authors__user__username__icontains=query) |
            Q(authors__user__email__icontains=query) |
            Q(authors__user__laboratory__icontains=query)
        ).distinct()

    return render(request, 'main/all_posts.html', {
        'posts': posts,
        'form': form,
        'query': query
    })


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    authors = post.authors.all().order_by('order')

    return render(request, 'main/post_detail.html', {
        'post': post,
        'authors': authors
    })


@login_required
def user_posts(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    posts = Post.objects.filter(authors__user=user).order_by('-created_at')

    return render(request, 'main/user_posts.html', {
        'user': user,
        'posts': posts
    })


@login_required
def search(request):
    form = SearchForm(request.GET or None)
    results = {}
    query = request.GET.get('query', '')
    search_type = request.GET.get('search_type', 'posts')

    if query:
        if search_type == 'posts':
            results['posts'] = Post.objects.filter(
                Q(article_identification_number__icontains=query) |
                Q(comment__icontains=query) |
                Q(authors__user__username__icontains=query) |
                Q(authors__user__email__icontains=query) |
                Q(authors__user__laboratory__icontains=query)
            ).distinct().order_by('-created_at')
        else:
            results['users'] = User.objects.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(laboratory__icontains=query) |
                Q(position__icontains=query) |
                Q(academic_degree__icontains=query)
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
            Q(email__icontains=query) |
            Q(laboratory__icontains=query) |
            Q(position__icontains=query)
        )

    return render(request, 'main/all_users.html', {
        'users': users,
        'query': query
    })


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if not post.authors.filter(user=request.user).exists():
        messages.error(request, 'У вас нет прав для редактирования этой публикации.')
        return redirect('all_posts')

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Публикация успешно обновлена!')
            return redirect('post_detail', pk=post.pk)
    else:
        current_authors = [pa.user for pa in post.authors.all()]
        form = PostForm(instance=post, initial={'authors': current_authors})

    return render(request, 'main/edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if not post.authors.filter(user=request.user).exists():
        messages.error(request, 'У вас нет прав для удаления этой публикации.')
        return redirect('all_posts')

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Публикация успешно удалена!')
        return redirect('profile')

    return render(request, 'main/delete_post.html', {'post': post})