from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import UsernameField
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

# Register your models here.
from .models import BlogUser


class BlogUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_('password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Enter password again'), widget=forms.PasswordInput)

    class Meta:
        model = BlogUser
        # 必须显式列出后台新增时要用到的字段：Django 5.1+ 的 UserAdmin.add_fieldsets
        # 默认含 usable_password，本项目用的是普通 ModelForm，不带上就会 500。
        fields = ('username', 'email', 'nickname')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("passwords do not match"))
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.source = 'adminsite'
            user.save()
        return user


class BlogUserChangeForm(UserChangeForm):
    class Meta:
        model = BlogUser
        fields = '__all__'
        field_classes = {'username': UsernameField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BlogUserAdmin(UserAdmin):
    form = BlogUserChangeForm
    add_form = BlogUserCreationForm
    list_display = (
        'id',
        'avatar_tag',
        'nickname',
        'username',
        'email',
        'last_login',
        'date_joined',
        'source')
    list_display_links = ('id', 'username')
    ordering = ('-id',)
    search_fields = ('username', 'nickname', 'email')

    # 新增页也必须显式声明，丢掉 Django 默认 add_fieldsets 里的 usable_password
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'nickname', 'password1', 'password2'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('nickname', 'email')}),
        ('头像与背景', {
            'fields': ('avatar', 'background'),
            'description': '文件保存在 uploads/user/&lt;用户名&gt;/avatar/ 与 '
                           'uploads/user/&lt;用户名&gt;/Background/ 目录，'
                           '数据库只记录相对路径，前台登录后据此加载。',
        }),
        ('权限', {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions'),
        }),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )

    def avatar_tag(self, obj):
        """列表页显示头像缩略图。"""
        if obj.avatar:
            return format_html(
                '<img src="{}" alt="头像" '
                'style="width:32px;height:32px;border-radius:50%;object-fit:cover;'
                'border:1px solid rgba(128,128,128,.35);">', obj.avatar.url)
        return format_html('<span style="opacity:.5">—</span>')

    avatar_tag.short_description = '头像'
