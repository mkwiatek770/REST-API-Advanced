from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ('id',)
    list_display = ('id', 'email', 'name', 'is_staff')
    fieldsets = (
        (None, dict(fields=('email', 'password'))),
        (_('Personal Info'), dict(fields=('name',))),
        (_('Permissions'), dict(fields=('is_active', 'is_superuser', 'is_staff'))),
        (_('Dates'), dict(fields=('last_login',))),
    )
    add_fieldsets = (
        (None, dict(classes=('wide',), fields=('email', 'password1', 'password2'))),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)
admin.site.register(models.Recipe)
