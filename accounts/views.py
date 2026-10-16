import logging
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView

from teachingplatform.utils import send_email, get_sha256, get_current_site, generate_code, delete_sidebar_cache
from teachingplatform.base_views import SecureFormView, LoginFormView, LogoutRedirectView
from . import utils
from .forms import RegisterForm, LoginForm, ForgetPasswordForm, ForgetPasswordCodeForm, ProfileForm
from .models import BlogUser

logger = logging.getLogger(__name__)


# Create your views here.

class RegisterView(SecureFormView):
    """
    用户注册视图（重构版）

    使用 SecureFormView 基类，自动提供 CSRF 保护
    """
    form_class = RegisterForm
    template_name = 'account/registration_form.html'

    def form_valid(self, form):
        if form.is_valid():
            user = form.save(False)
            user.is_active = False
            user.source = 'Register'
            user.save(True)
            site = get_current_site().domain
            sign = get_sha256(get_sha256(settings.SECRET_KEY + str(user.id)))

            if settings.DEBUG:
                site = '127.0.0.1:8000'
            path = reverse('account:result')
            url = "http://{site}{path}?type=validation&id={id}&sign={sign}".format(
                site=site, path=path, id=user.id, sign=sign)

            content = """
                            <p>请点击下面链接验证您的邮箱</p>

                            <a href="{url}" rel="bookmark">{url}</a>

                            再次感谢您！
                            <br />
                            如果上面链接无法打开，请将此链接复制至浏览器。
                            {url}
                            """.format(url=url)
            send_email(
                emailto=[
                    user.email,
                ],
                title='验证您的电子邮箱',
                content=content)

            url = reverse('accounts:result') + \
                  '?type=register&id=' + str(user.id)
            return HttpResponseRedirect(url)
        else:
            return self.render_to_response({
                'form': form
            })


class LogoutView(LogoutRedirectView):
    """
    用户登出视图（重构版）

    使用 LogoutRedirectView 基类，自动禁用缓存
    """
    url = '/login/'

    def get(self, request, *args, **kwargs):
        logout(request)
        delete_sidebar_cache()
        # 获取响应对象并删除登录标记 cookie
        response = super(LogoutView, self).get(request, *args, **kwargs)
        response.delete_cookie('logged_user')
        return response


class LoginView(LoginFormView):
    """
    统一登录入口（前台 / 后台共用 /login/）

    平台不区分「用户登录」和「管理员登录」两个页面，只在 /login/ 判断一次：
    认证成功后读取数据库中的管理员标志（BlogUser.is_superuser），
    是管理员则进入后台管理，否则回到前台。

    使用 LoginFormView 基类，自动提供：
    - 敏感参数保护（password）
    - CSRF 保护
    - 禁用缓存
    """
    form_class = LoginForm
    template_name = 'account/login.html'
    success_url = '/'
    redirect_field_name = REDIRECT_FIELD_NAME

    # ---------- 落点决策 ----------

    def _admin_index(self):
        return reverse('admin:index')

    def _is_safe_target(self, target):
        """只接受指向本站的地址，避免被构造成开放重定向。"""
        return bool(target) and url_has_allowed_host_and_scheme(
            url=target,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure())

    def _is_admin_target(self, target):
        return self._is_safe_target(target) and target.startswith(
            self._admin_index())

    def resolve_redirect(self, user, target):
        """根据是否为管理员决定登录后的落点。

        - 管理员：优先回到原本想访问的页面，否则进后台首页；
        - 普通用户：优先回到原本想访问的前台页面，否则进首页。
          指向后台的 next 会被丢弃，否则会被后台权限校验反复弹回登录页，
          与登录页形成无限重定向。

        空值或首页视为「未指定目标」，此时管理员进后台、普通用户进前台，
        这正是「按数据库管理员标志分流」的默认行为。
        """
        admin_index = self._admin_index()
        if not target or target == self.success_url:
            return admin_index if user.is_platform_admin else self.success_url
        if user.is_platform_admin:
            return target if self._is_safe_target(target) else admin_index
        if self._is_safe_target(target) and not self._is_admin_target(target):
            return target
        return self.success_url

    # ---------- 视图 ----------

    def get(self, request, *args, **kwargs):
        # 已登录用户再访问登录页时，直接送往对应的大厅
        if request.user.is_authenticated:
            target = request.GET.get(self.redirect_field_name)
            return HttpResponseRedirect(
                self.resolve_redirect(request.user, target))
        return super(LoginView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        redirect_to = self.request.GET.get(
            self.redirect_field_name) or self.success_url
        kwargs['redirect_to'] = redirect_to
        # 供模板切换文案：从后台被弹过来时提示管理员登录
        kwargs['is_admin_login'] = self._is_admin_target(redirect_to)

        return super(LoginView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        form = AuthenticationForm(data=self.request.POST, request=self.request)

        if form.is_valid():
            delete_sidebar_cache()
            logger.info(self.redirect_field_name)

            auth.login(self.request, form.get_user())
            # 设置登录有效期
            if self.request.POST.get("remember"):
                self.request.session.set_expiry(settings.REMEMBER_ME_LOGIN_TTL)
                cookie_max_age = settings.REMEMBER_ME_LOGIN_TTL
            else:
                # 使用Django默认的2周
                self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                cookie_max_age = settings.SESSION_COOKIE_AGE

            # 获取响应对象并设置登录标记 cookie
            response = super(LoginView, self).form_valid(form)
            response.set_cookie(
                'logged_user',
                'true',
                max_age=cookie_max_age,
                httponly=False,  # 允许 JavaScript 访问
                samesite='Lax'
            )
            return response
            # return HttpResponseRedirect('/')
        else:
            return self.render_to_response({
                'form': form
            })

    def get_success_url(self):
        target = self.request.POST.get(self.redirect_field_name)
        return self.resolve_redirect(self.request.user, target)


def account_result(request):
    type = request.GET.get('type')
    id = request.GET.get('id')

    user = get_object_or_404(get_user_model(), id=id)
    logger.info(type)
    if user.is_active:
        return HttpResponseRedirect('/')
    if type and type in ['register', 'validation']:
        if type == 'register':
            content = '''
    恭喜您注册成功，一封验证邮件已经发送到您的邮箱，请验证您的邮箱后登录本站。
    '''
            title = '注册成功'
        else:
            c_sign = get_sha256(get_sha256(settings.SECRET_KEY + str(user.id)))
            sign = request.GET.get('sign')
            if sign != c_sign:
                return HttpResponseForbidden()
            user.is_active = True
            user.save()
            content = '''
            恭喜您已经成功的完成邮箱验证，您现在可以使用您的账号来登录本站。
            '''
            title = '验证成功'
        return render(request, 'account/result.html', {
            'title': title,
            'content': content
        })
    else:
        return HttpResponseRedirect('/')


class ForgetPasswordView(SecureFormView):
    """
    忘记密码视图（重构版）

    使用 SecureFormView 基类，自动提供 CSRF 保护
    """
    form_class = ForgetPasswordForm
    template_name = 'account/forget_password.html'

    def form_valid(self, form):
        if form.is_valid():
            blog_user = BlogUser.objects.filter(email=form.cleaned_data.get("email")).get()
            blog_user.password = make_password(form.cleaned_data["new_password2"])
            blog_user.save()
            return HttpResponseRedirect('/login/')
        else:
            return self.render_to_response({'form': form})


class ForgetPasswordEmailCode(View):

    def post(self, request: HttpRequest):
        form = ForgetPasswordCodeForm(request.POST)
        if not form.is_valid():
            return HttpResponse("错误的邮箱")
        to_email = form.cleaned_data["email"]

        code = generate_code()
        utils.send_verify_email(to_email, code)
        utils.set_code(to_email, code)

        return HttpResponse("ok")


class ProfileView(LoginRequiredMixin, UpdateView):
    """个人资料页：修改昵称/邮箱，上传头像与个人背景图。

    只允许操作 ``request.user`` 自己，避免通过改 URL 编辑别人的资料。
    """

    model = BlogUser
    form_class = ProfileForm
    template_name = 'account/profile.html'
    login_url = '/login/'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('saved', False)
        return context

    def form_valid(self, form):
        self.object = form.save()
        # 保存成功后直接回到本页并给出提示（不依赖 messages 框架）
        return self.render_to_response(
            self.get_context_data(form=form, saved=True))
