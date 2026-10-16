# -*- coding: utf-8 -*-
"""写入默认导航项。

改造后前台顶部导航完全由 blog.NavItem 驱动（模板里不再写死「首页 / 资源归档」），
所以这里用 get_or_create 补上三个默认项，保证升级后导航外观与改造前一致：

    首页  →  全部分类（自动展开课程分类）  →  资源归档

使用 get_or_create，重复执行安全；也不会覆盖管理员后来改过的内容。
"""
from django.db import migrations


DEFAULTS = (
    # (名称, 链接类型, 排序)
    ('首页', 'index', 0),
    ('全部分类', 'categories', 10),
    ('资源归档', 'archives', 100),
)


def create_default_nav_items(apps, schema_editor):
    NavItem = apps.get_model('blog', 'NavItem')
    for name, target_type, order in DEFAULTS:
        NavItem.objects.get_or_create(
            name=name,
            defaults={
                'target_type': target_type,
                'order': order,
                'is_enable': True,
            },
        )


def remove_default_nav_items(apps, schema_editor):
    NavItem = apps.get_model('blog', 'NavItem')
    NavItem.objects.filter(name__in=[d[0] for d in DEFAULTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_alter_navitem_target_type'),
    ]

    operations = [
        migrations.RunPython(create_default_nav_items, remove_default_nav_items),
    ]
