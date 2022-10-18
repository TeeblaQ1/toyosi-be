from django.contrib import admin

# Register your models here.
from authentication.models import Profile, User

class UserProfileInline(admin.TabularInline):
    model = Profile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_verified', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    inlines = [UserProfileInline]