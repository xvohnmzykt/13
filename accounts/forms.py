from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.utils.translation import gettext_lazy as _
from . import utils
from .models import BlogUser


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = widgets.TextInput(
            attrs={'placeholder': "username", "class": "form-control"})
        self.fields['password'].widget = widgets.PasswordInput(
            attrs={'placeholder': "password", "class": "form-control"})


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget = widgets.TextInput(
            attrs={'placeholder': "username", "class": "form-control"})
        self.fields['email'].widget = widgets.EmailInput(
            attrs={'placeholder': "email", "class": "form-control"})
        self.fields['password1'].widget = widgets.PasswordInput(
            attrs={'placeholder': "password", "class": "form-control"})
        self.fields['password2'].widget = widgets.PasswordInput(
            attrs={'placeholder': "repeat password", "class": "form-control"})

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError(_("email already exists"))
        return email

    class Meta:
        model = get_user_model()
        fields = ("username", "email")


class ForgetPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                'placeholder': _("New password")
            }
        ),
    )

    new_password2 = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                'placeholder': _("Confirm password")
            }
        ),
    )

    email = forms.EmailField(
        label='邮箱',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _("Email")
            }
        ),
    )

    code = forms.CharField(
        label=_('Code'),
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _("Code")
            }
        ),
    )

    def clean_new_password2(self):
        password1 = self.data.get("new_password1")
        password2 = self.data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("passwords do not match"))
        password_validation.validate_password(password2)

        return password2

    def clean_email(self):
        user_email = self.cleaned_data.get("email")
        if not BlogUser.objects.filter(
                email=user_email
        ).exists():
            # todo 这里的报错提示可以判断一个邮箱是不是注册过，如果不想暴露可以修改
            raise ValidationError(_("email does not exist"))
        return user_email

    def clean_code(self):
        code = self.cleaned_data.get("code")
        error = utils.verify(
            email=self.cleaned_data.get("email"),
            code=code,
        )
        if error:
            raise ValidationError(error)
        return code


class ForgetPasswordCodeForm(forms.Form):
    email = forms.EmailField(
        label=_('Email'),
    )


class ChineseClearableFileInput(forms.ClearableFileInput):
    """带中文提示的「可清除」文件控件。"""
    initial_text = '当前文件'
    input_text = '更换为'
    clear_checkbox_label = '清除'


class ProfileForm(forms.ModelForm):
    """个人资料：修改昵称/邮箱，并上传头像与个人背景图。

    头像保存到 ``user/<账号>/avatar/``，背景图保存到 ``user/<账号>/Background/``，
    路径由 BlogUser 上的 upload_to 决定，数据库只存相对 MEDIA_ROOT 的路径。
    """

    MAX_AVATAR_MB = 5
    MAX_BACKGROUND_MB = 10
    IMAGE_TYPES = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')

    class Meta:
        model = BlogUser
        fields = ('nickname', 'email', 'avatar', 'background')
        labels = {
            'nickname': '昵称',
            'email': '邮箱',
            'avatar': '头像',
            'background': '个人背景图',
        }
        widgets = {
            'nickname': widgets.TextInput(attrs={'placeholder': '留空则显示用户名'}),
            'email': widgets.EmailInput(attrs={'placeholder': '用于找回密码'}),
            'avatar': ChineseClearableFileInput(attrs={
                'class': 'upload-input', 'accept': 'image/*'}),
            'background': ChineseClearableFileInput(attrs={
                'class': 'upload-input', 'accept': 'image/*'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            taken = BlogUser.objects.filter(email=email).exclude(pk=self.instance.pk)
            if taken.exists():
                raise ValidationError('该邮箱已被其他账号使用')
        return email

    def _validate_image(self, image, max_mb, label):
        if not image:
            return image
        # 已存在的文件（FileField 回填）没有 size，跳过校验
        size = getattr(image, 'size', None)
        if size and size > max_mb * 1024 * 1024:
            raise ValidationError('{}不能超过 {} MB'.format(label, max_mb))
        name = getattr(image, 'name', '') or ''
        if '.' in name and not name.lower().endswith(self.IMAGE_TYPES):
            raise ValidationError('{}只支持图片格式：{}'.format(
                label, '、'.join(self.IMAGE_TYPES)))
        return image

    def clean_avatar(self):
        return self._validate_image(
            self.cleaned_data.get('avatar'), self.MAX_AVATAR_MB, '头像')

    def clean_background(self):
        return self._validate_image(
            self.cleaned_data.get('background'), self.MAX_BACKGROUND_MB, '背景图')
