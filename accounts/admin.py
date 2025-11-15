from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import User, Passenger


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理界面"""
    list_display = ('username', 'email', 'phone', 'role', 'is_active', 'date_joined', 'last_login', 'avatar_display')
    list_filter = ('role', 'is_active', 'date_joined', 'gender')
    search_fields = ('username', 'email', 'phone', 'real_name', 'id_card')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('个人信息'), {'fields': ('email', 'phone', 'real_name', 'id_card', 'gender', 'address', 'avatar')}),
        (_('权限'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('重要日期'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'phone', 'role', 'real_name', 'gender'),
        }),
    )
    
    def avatar_display(self, obj):
        """在列表中显示头像缩略图"""
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.avatar.url)
        return "无头像"
    
    avatar_display.short_description = '头像'


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    """乘客管理界面"""
    list_display = ('name', 'id_card', 'gender', 'birth_date', 'user', 'created_at')
    list_filter = ('gender', 'created_at')
    search_fields = ('name', 'id_card', 'passport_number')
    raw_id_fields = ('user',)
