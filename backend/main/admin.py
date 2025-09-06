from django.contrib import admin
from .models import Publication

@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at']
    list_filter = ['created_at', 'author']
    search_fields = ['title', 'content']