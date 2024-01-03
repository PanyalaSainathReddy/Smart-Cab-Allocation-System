from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Google', {'fields': ('is_google',)}),
    )

    list_display = UserAdmin.list_display + ('is_google',)
    list_filter = UserAdmin.list_filter + ('is_google',)

    class Meta:
        model = User

admin.site.register(User, CustomUserAdmin)
