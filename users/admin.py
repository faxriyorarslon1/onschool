from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('username', 'last_name', 'middlename',
                                         'dob','phone', 'gender', 'course')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'username', 'last_name', 'middlename', 'dob', 'phone', 'gender', 'course'),
        }),
    )
    list_display = ('name', 'phone', 'group', 'is_staff')
    search_fields = ('email', 'username', 'last_name')
    ordering = ('-id',)

    def name(self, ins):
        return ins.username+" "+ins.last_name

    def group(self, user):
        groups = []
        for group in user.groups.all():
            groups.append(group.name)
        return ' '.join(groups)
    group.short_description = 'Groups'
