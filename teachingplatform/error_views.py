#!/usr/bin/env python
# encoding: utf-8

"""
Django Blog 统一错误处理视图
提供统一的错误页面渲染，减少重复代码
"""

import logging
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


def render_error_page(request, status_code, message, exception=None):
    """
    通用错误页面渲染函数

    统一处理各种 HTTP 错误，提供一致的错误页面展示

    Args:
        request: HTTP 请求对象
        status_code: HTTP 状态码（404, 403, 500等）
        message: 错误消息（支持国际化）
        exception: 异常对象（可选），会被记录到日志

    Returns:
        HttpResponse: 渲染后的错误页面

    Usage:
        def my_error_handler(request, exception):
            return render_error_page(request, 404, "Page not found", exception)
    """
    if exception:
        logger.error(
            f'HTTP {status_code} Error: {exception}',
            exc_info=True,
            extra={
                'request': request,
                'status_code': status_code
            }
        )

    return render(
        request,
        'blog/error_page.html',
        {
            'message': message,
            'statuscode': str(status_code)
        },
        status=status_code
    )


def page_not_found_view(request, exception, template_name='blog/error_page.html'):
    """
    404 错误页面处理器

    当用户访问不存在的页面时显示

    Args:
        request: HTTP 请求对象
        exception: 异常对象
        template_name: 模板名称（保留参数以兼容 Django 标准）

    Returns:
        HttpResponse: 404 错误页面
    """
    return render_error_page(
        request,
        404,
        _('Sorry, the page you requested is not found, please click the home page to see other?'),
        exception
    )


def server_error_view(request, template_name='blog/error_page.html'):
    """
    500 错误页面处理器

    当服务器内部错误时显示

    Args:
        request: HTTP 请求对象
        template_name: 模板名称（保留参数以兼容 Django 标准）

    Returns:
        HttpResponse: 500 错误页面
    """
    return render_error_page(
        request,
        500,
        _('Sorry, the server is busy, please click the home page to see other?')
    )


def permission_denied_view(request, exception, template_name='blog/error_page.html'):
    """
    403 错误页面处理器

    当用户无权限访问时显示

    Args:
        request: HTTP 请求对象
        exception: 异常对象
        template_name: 模板名称（保留参数以兼容 Django 标准）

    Returns:
        HttpResponse: 403 错误页面
    """
    return render_error_page(
        request,
        403,
        _('Sorry, you do not have permission to access this page?'),
        exception
    )


def bad_request_view(request, exception, template_name='blog/error_page.html'):
    """
    400 错误页面处理器

    当请求格式错误时显示

    Args:
        request: HTTP 请求对象
        exception: 异常对象
        template_name: 模板名称（保留参数以兼容 Django 标准）

    Returns:
        HttpResponse: 400 错误页面
    """
    return render_error_page(
        request,
        400,
        _('Sorry, the request was invalid?'),
        exception
    )


def csrf_failure_view(request, reason=''):
    """CSRF 校验失败时的友好提示页。

    Django 自带的失败页在 DEBUG=True 时会输出一大段机制说明，对普通用户没有意义。
    这里统一渲染成平台自身的错误页，并提示最可能的原因与处理办法：
    登录 / 登出会轮换 CSRF token，提交登录前渲染的旧页面（旧标签页、浏览器后退）
    就会得到 "CSRF token from POST incorrect"。
    """
    logger.warning('CSRF failure on %s: %s', request.path, reason)

    response = render(
        request,
        'blog/error_page.html',
        {
            'message': '页面已过期，请重新登录',
            'hint': '为保证安全，登录或登出后表单校验令牌会更换。'
                    '浏览器后退、或停留在旧标签页中的登录表单已经失效，'
                    '请点下面的按钮重新打开登录页。',
            'statuscode': '403',
            'show_login_link': True,
        },
        status=403
    )
    # 让浏览器不要复用这份已失效的页面，避免再次提交同样的旧表单
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
    return response
