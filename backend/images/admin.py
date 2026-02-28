from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Image, UserActivity

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action', 'timestamp')
    list_filter = ('timestamp', 'action')
    search_fields = ('user__username', 'action')