from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Post, PostAuthor

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'laboratory', 'position', 'is_admin']
    list_filter = ['is_admin', 'status', 'laboratory']
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': (
                'laboratory', 'year_of_birth', 'year_of_graduation',
                'academic_degree', 'year_of_degree', 'status',
                'position', 'title', 'fte', 'is_admin'
            )
        }),
    )

class PostAuthorInline(admin.TabularInline):
    model = PostAuthor
    extra = 1

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['type', 'year', 'status', 'created_at']
    list_filter = ['type', 'status', 'year']
    search_fields = ['article_identification_number', 'comment']
    inlines = [PostAuthorInline]

@admin.register(PostAuthor)
class PostAuthorAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'order']
    list_filter = ['post__type']