from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from teachingplatform.utils import get_current_site


# Create your models here.

def user_avatar_path(instance, filename):
    """头像上传路径：``user/<账号>/avatar/<文件名>``（相对于 MEDIA_ROOT）。"""
    return 'user/{username}/avatar/{filename}'.format(
        username=instance.username, filename=filename)


def user_background_path(instance, filename):
    """背景图上传路径：``user/<账号>/Background/<文件名>``（相对于 MEDIA_ROOT）。"""
    return 'user/{username}/Background/{filename}'.format(
        username=instance.username, filename=filename)


class BlogUser(AbstractUser):
    nickname = models.CharField(_('nick name'), max_length=100, blank=True)
    creation_time = models.DateTimeField(_('creation time'), default=now)
    last_modify_time = models.DateTimeField(_('last modify time'), default=now)
    source = models.CharField(_('create source'), max_length=100, blank=True)

    # 这两个字段的 label 直接用中文，免去额外维护 .po 词条
    avatar = models.ImageField(
        '头像',
        upload_to=user_avatar_path,
        blank=True,
        null=True,
        help_text='上传后保存在 user/<账号>/avatar/ 目录')
    background = models.ImageField(
        '背景图',
        upload_to=user_background_path,
        blank=True,
        null=True,
        help_text='上传后保存在 user/<账号>/Background/ 目录，登录后作为个人背景显示')

    def get_absolute_url(self):
        return reverse(
            'blog:author_detail', kwargs={
                'author_name': self.username})

    @property
    def is_platform_admin(self):
        """是否为平台管理员。

        直接取自数据库字段 ``is_superuser``（后台 AdminSite 也以该字段作为准入依据），
        统一登录入口用它决定登录成功后进入后台管理还是前台首页。
        若要改为「职员即可进后台」，只需把这里改成 ``self.is_staff``。
        """
        return bool(self.is_superuser and self.is_active)

    @property
    def display_name(self):
        """优先显示昵称，没有昵称时退回用户名。"""
        return self.nickname or self.username

    @property
    def avatar_url(self):
        """头像地址；未上传时返回空字符串，由模板决定回退到默认头像。"""
        return self.avatar.url if self.avatar else ''

    @property
    def background_url(self):
        """背景图地址；未上传时返回空字符串。"""
        return self.background.url if self.background else ''

    def save(self, *args, **kwargs):
        """保存时清理被替换掉的旧头像/旧背景图，避免 uploads 目录堆积无用文件。"""
        if self.pk:
            old = BlogUser.objects.filter(pk=self.pk).only(
                'avatar', 'background').first()
            if old is not None:
                for field in ('avatar', 'background'):
                    old_file = getattr(old, field)
                    new_file = getattr(self, field)
                    if old_file and old_file.name != new_file.name:
                        old_file.storage.delete(old_file.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

    def get_full_url(self):
        site = get_current_site().domain
        url = "https://{site}{path}".format(site=site,
                                            path=self.get_absolute_url())
        return url

    class Meta:
        ordering = ['-id']
        verbose_name = _('user')
        verbose_name_plural = verbose_name
        get_latest_by = 'id'
