# 在线教学资源平台的设计与实现

基于 Python + Django 的在线教学资源平台。系统面向教师与学生，提供课程资源发布、分类检索、全文搜索、
评论互动、资源收藏与后台管理等能力，实现了从资源生产到资源消费的完整闭环。

---

## 一、项目简介

本系统是一个 B/S 架构的在线教学资源平台。教师可在后台创建课程分类、上传教学资源（课件、讲义、
教学视频链接、实验指导书等），学生可在前台按分类、标签浏览与检索资源，并对资源发表评论。
系统同时提供全文检索、热门资源统计、资源推荐、深浅色主题切换等功能。

## 二、功能模块

| 模块 | 说明 |
| --- | --- |
| 用户模块 | 注册、登录、找回密码、邮箱验证码、个人资料与头像、基于邮箱或用户名的登录；前台与后台共用 `/login/` 统一入口，登录后按数据库管理员标志自动分流 |
| 教学资源模块 | 资源的增删改查、草稿与发布状态、置顶排序、目录导航、阅读量统计、Markdown 正文、代码高亮 |
| 课程分类与标签 | 多级课程分类、资源标签、分类导航菜单、按分类 / 标签 / 作者归档检索 |
| 全文检索 | 基于 Whoosh（默认）或 Elasticsearch 的中文分词全文检索，支持关键词高亮 |
| 评论模块 | 多级嵌套评论、Markdown 评论、评论审核开关、评论邮件通知、表情与点赞 |
| 平台配置模块 | 平台名称、简介、SEO 关键词、备案号、统计代码、配色方案等可视化配置 |
| 插件系统 | 基于钩子的插件机制，内置浏览计数、资源推荐、版权声明、外链处理、图片懒加载、阅读时长等插件 |
| 后台管理 | 独立的 AdminSite，支持资源的批量发布 / 下架、评论管理、用户管理、邮件日志、系统命令 |
| 运维支撑 | 站点地图、RSS 订阅、搜索引擎推送、缓存管理、健康检查接口、异常邮件告警 |

## 三、技术栈

| 层次 | 技术选型 |
| --- | --- |
| 后端框架 | Python 3.12、Django 5.2 |
| 数据库 | MySQL 8.0（utf8mb4），可切换 SQLite |
| 缓存 | LocMemCache（默认）/ Redis |
| 全文检索 | Whoosh 2.7（默认）/ Elasticsearch 8.x |
| 前端 | Alpine.js 3、Tailwind CSS 3、HTMX 2、Vite 6 |
| 富文本编辑 | django-mdeditor（Markdown） |
| 部署 | Gunicorn + Nginx / Docker / Kubernetes |

## 四、系统架构

```
浏览器 (Tailwind + Alpine.js + HTMX)
        │  HTTP / HTMX 局部刷新
        ▼
Django URL 路由 (teachingplatform/urls.py)
        │
        ├── blog        教学资源、课程分类、标签、平台配置
        ├── accounts    用户与认证
        ├── comments    评论
        ├── oauth       第三方登录
        ├── servermanager  运维命令与邮件日志
        └── plugins     插件（钩子注册）
        │
        ├── MySQL        业务数据
        ├── Whoosh/ES    全文索引
        └── Cache        页面与片段缓存
```

## 五、数据库设计

采用 MySQL 8.0，字符集 `utf8mb4`。核心数据表如下：

| 表名 | 说明 | 关键字段 |
| --- | --- | --- |
| `blog_article` | 教学资源主表 | `title` 标题、`body` 正文、`pub_time` 发布时间、`status` 状态（草稿/发布）、`type` 类型（资源/单页）、`views` 浏览量、`author_id` 发布者、`category_id` 所属分类 |
| `blog_category` | 课程分类 | `name` 名称、`parent_category_id` 父分类、`index` 排序 |
| `blog_tag` | 资源标签 | `name` 标签名 |
| `blog_article_tags` | 资源—标签关联表 | `article_id`、`tag_id` |
| `blog_blogsettings` | 平台配置 | `site_name` 平台名称、`site_description` 平台简介、`site_keywords` 关键词、`color_scheme` 配色、`beian_code` 备案号 |
| `blog_links` | 友情链接 | `name`、`link`、`show_type` 展示位置 |
| `blog_sidebar` | 侧边栏配置 | `name`、`content`、`sequence` |
| `accounts_bloguser` | 平台用户 | `username`、`email`、`nickname`、`avatar` |
| `comments_comment` | 评论 | `article_id`、`body`、`parent_comment_id` 父评论、`is_enable` 是否显示 |
| `comments_commentreaction` | 评论点赞 | `comment_id`、`user_id` |
| `oauth_oauthuser` / `oauth_oauthconfig` | 第三方登录绑定与配置 | `openid`、`oauth_type` |
| `servermanager_command` / `emailsendlog` | 运维命令与邮件发送日志 | `command`、`email`、`send_time` |

创建数据库：

```sql
CREATE DATABASE `teaching_resource` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

数据库连接信息**不写在代码里**，而是从环境变量读取；项目根目录下的 `.env` 文件会在
`settings.py` 启动时自动载入（该文件已加入 `.gitignore`，不会提交到仓库）：

```bash
# 首次运行时，从模板复制一份
cp .env.example .env        # Windows: copy .env.example .env
# 然后编辑 .env，填入本机真实的数据库密码
```

可用的变量如下：

| 环境变量 | 说明 | 默认值 |
| --- | --- | --- |
| `DJANGO_MYSQL_DATABASE` | 数据库名 | `teaching_resource` |
| `DJANGO_MYSQL_USER` | 数据库用户 | `root` |
| `DJANGO_MYSQL_PASSWORD` | 数据库密码 | 空（必须由 `.env` 或系统环境变量提供） |
| `DJANGO_MYSQL_HOST` | 数据库地址 | `127.0.0.1` |
| `DJANGO_MYSQL_PORT` | 数据库端口 | `3306` |
| `DJANGO_SECRET_KEY` | Django 密钥 | 内置开发用默认值 |
| `DJANGO_DEBUG` | 调试开关 | `True` |

## 六、目录结构

```
.
├── manage.py                  Django 管理入口
├── requirements.txt           后端依赖清单
├── .env.example               环境变量模板（复制为 .env 后填入本机配置）
├── start.bat / manage.bat     Windows 启动脚本与命令包装
├── teachingplatform/          项目配置包（settings / urls / wsgi / 工具与插件管理）
│   ├── settings.py            全局配置
│   ├── urls.py                总路由
│   ├── admin_site.py          自定义后台站点
│   └── plugin_manage/         插件钩子框架
├── blog/                      教学资源核心应用（模型、视图、模板标签）
├── accounts/                  用户与认证
├── comments/                  评论
├── oauth/                     第三方登录
├── servermanager/             运维与邮件
├── plugins/                   插件实现
├── templates/                 页面模板
├── locale/                    多语言词条（中文 / 繁体 / 英文）
├── frontend/                  前端工程（Vite + Tailwind + Alpine.js + HTMX）
└── deploy/                    部署脚本与配置
```

## 七、运行环境

| 组件 | 版本要求 |
| --- | --- |
| Python | 3.10 及以上（本项目在 3.12 上验证） |
| MySQL | 5.7 / 8.0 |
| Node.js | 18 及以上（仅构建前端资源时需要） |

## 八、安装与运行

### 1. 安装后端依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

在 MySQL 中创建数据库（见上文「数据库设计」），然后把 `.env.example` 复制为 `.env`
并填入本机数据库密码：

```bash
cp .env.example .env        # Windows: copy .env.example .env
```

`.env` 不纳入版本控制，因此仓库里不会出现任何真实凭据。

### 3. 初始化数据表

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 创建管理员账号

```bash
python manage.py createsuperuser
```

### 5. 构建前端资源

```bash
cd frontend
npm install
npm run build
cd ..
```

### 6. 收集静态文件并启动服务

```bash
python manage.py collectstatic --noinput
python manage.py runserver
```

浏览器访问 <http://127.0.0.1:8000/> 进入平台首页；后台管理同样从这里登录。

### 7. 可选：生成演示数据

```bash
python manage.py create_testdata
```

## 九、登录与权限

### 9.1 统一登录入口

平台**只有一个登录页面 `/login/`**，前台用户与管理员共用，不存在单独的"后台登录页"：

1. 管理员直接访问 `/admin/` 时，会被重定向到 `/login/?next=/admin/`；
2. 在 `/login/` 提交账号密码后，系统读取数据库中的管理员标志
   （`BlogUser.is_superuser`，封装为 `BlogUser.is_platform_admin`）判断身份：
   - **管理员** → 进入后台管理 `/admin/`（若原本要访问某个后台页面则回到该页）；
   - **普通用户** → 返回前台首页（或原本要访问的前台页面）。
3. 已经登录的用户再打开 `/login/`，会直接送往对应的首页。

管理员登录后，**前台导航栏右上角会出现「后台管理」按钮**（移动端菜单里也有一个入口），
随时可以从前台跳回后台；普通用户和未登录访客看不到该入口。侧边栏「功能」卡片中也保留了
同样的入口。

> 判断依据是数据库字段而非 URL。若希望"职员即可进后台"，只需把
> `accounts/models.py` 中 `is_platform_admin` 的 `self.is_superuser` 改成 `self.is_staff`，
> 登录分流与后台准入会同步生效（后台的 `has_permission` 复用了同一属性）。

安全性上有两点处理：`next` 参数只接受本站地址（防开放重定向）；普通用户携带
`next=/admin/` 时该参数会被丢弃，避免被后台权限校验反复弹回登录页而出现无限重定向。

### 9.2 后台管理

后台地址：`/admin/`，仅管理员可进入。主要功能：
- **教学资源**：新增、编辑、批量发布 / 设为草稿、设置置顶排序、开启或关闭评论
- **课程分类 / 标签**：维护多级分类体系与标签库
- **评论**：审核、隐藏、回复
- **平台配置**：平台名称、简介、SEO 关键词、备案号、统计代码、配色方案
- **用户**：创建、禁用、重置密码
- **导航菜单**：自定义前台顶部导航（见下）
- **插件**：查看已加载插件及其元信息

#### 导航菜单（可自定义前台导航）

后台 `BLOG → 导航菜单` 可对前台顶部导航做完整的增删改查，字段如下：

| 字段 | 说明 |
| --- | --- |
| 名称 | 导航上显示的文字 |
| 链接类型 | 首页 / 全部分类 / 资源归档 / 课程分类 / 单页 / 自定义链接 |
| 自定义链接 | 类型选「自定义链接」时填写；站内路径以 `/` 开头，外链写完整地址 |
| 课程分类 / 单页 | 类型选「课程分类」或「单页」时指定具体对象 |
| 上级菜单 | 选择后本项变成该项的下拉子项（支持二级菜单） |
| 排序 | 数值越小越靠前，列表页可直接编辑 |
| 启用 | 取消勾选即从导航隐藏，无需删除 |
| 新窗口打开 | 前台以 `target="_blank"` 打开 |

**顶部导航（桌面端与移动端）完全由这张表驱动，模板里不再写死任何导航项。**
改造前「首页 / 资源归档」是硬编码在 `nav.html` 里的，现在它们是两条默认导航项，
可以在后台改名、排序、停用或删除。

其中「**全部分类**」是一个会自动展开的特殊类型：它会按 `课程分类` 表的数据
渲染出分类及子分类下拉，所以**新增分类依然会自动出现在导航里**，无需手工加导航项。

迁移 `0011_seed_default_navitems` 会用 `get_or_create` 补上三条默认项，保证升级后
导航外观与改造前一致（重复执行安全，也不会覆盖已修改的内容）：

| 名称 | 链接类型 | 排序 |
| --- | --- | --- |
| 首页 | 首页 | 0 |
| 全部分类 | 全部分类 | 10 |
| 资源归档 | 资源归档 | 100 |

实现涉及三处：模型 `blog.models.NavItem`、后台 `blog.admin.NavItemAdmin`、
模板 `templates/share_layout/nav.html`；导航数据由 `blog/context_processors.py` 提供。

> **缓存提醒**：本项目用的是 `LocMemCache`（进程内缓存），导航数据会缓存 10 小时。
> 通过**后台**修改导航项时，`NavItemAdmin` 会自动 `cache.clear()`，改动立即生效；
> 但如果你是用外部脚本直接改数据库，清的只是脚本自己进程的缓存，
> runserver 进程那份仍在——此时需要重启服务。
> 生产环境若用多进程（如 gunicorn 多 worker），`LocMemCache` 会导致各 worker
> 缓存不一致，建议改用 `FileBasedCache` 或 Redis。

**增删改查（CRUD）**：教学内容模型均支持完整的增、删、改、查：

| 模型 | 增 | 改 | 删 | 查 |
| --- | --- | --- | --- | --- |
| 教学资源 / 课程分类 / 标签 / 链接 / 侧边栏 | ✅ | ✅ | ✅ 单个 + 批量 | ✅ 搜索 + 过滤 |
| 评论 | ✅ | ✅ | ✅ 单个 + 批量 | ✅ 搜索 + 过滤 |
| 用户 | ✅ | ✅ | ✅ | ✅ |
| OAuth 配置 / 站点 / 运维命令 | ✅ | ✅ | ✅ | ✅ |

少数模型按设计限制操作：**平台配置**（单例，只能修改）、**邮件发送 log**（日志，不可新增）、
**第三方用户**（绑定关系，不可新增）、**日志记录**（审计日志，只读）。

两个容易踩的坑，改后台代码时请注意：

1. **自定义 `actions` 会整体替换 Django 的默认动作列表**，必须显式写回 `'delete_selected'`，
   否则列表页就没有「删除所选」。`blog/admin.py` 与 `comments/admin.py` 已处理。
2. **`exclude` 里的字段名必须与模型字段完全一致。** 本项目里 `Article` / `Category` / `Tag`
   继承 `BaseModel`（字段名 `last_modify_time`），而 `Links` / `SideBar` 直接继承 `Model`
   （字段名 `last_mod_time`），写错会导致该字段既没被排除、又因 `blank=False` 变成必填，
   保存时报「该字段是必填项」而无法新增。

> 另外，Django 在**列表为空时不会渲染动作下拉框**，这是正常行为，新增一条数据后即可看到。

### 9.3 账号说明

- **管理员**：用 `python manage.py createsuperuser` 创建，或参考「安装与运行」第 4 步。
- **普通用户**：`python manage.py create_testdata` 会创建一个演示用的普通用户；
  也可以在后台「用户」里自行新增（该模型增删改查齐全）。

出于安全考虑，仓库中不放任何可用口令。首次部署请务必自行创建管理员并设置强口令。

### 9.4 头像与个人背景图

登录后右上角显示**头像 + 用户名**，点击展开菜单（个人资料 / 后台管理 / 退出登录）。
头像与背景图都在 `/account/profile/` 上传，**每个账号一套，互不影响**。

**存储结构**（`MEDIA_ROOT` 默认为项目根下的 `uploads/`）：

```
uploads/
└── user/
    └── <用户名>/
        ├── avatar/         头像
        └── Background/     个人背景图
```

数据库只保存相对 `MEDIA_ROOT` 的路径（例如 `user/1/Background/user1-bg.png`），
模板通过 `user.avatar_url` / `user.background_url` 取用。登录后 `base.html` 会把该
账号的背景写到 `<body style="--user-background: url(...)">`，再由
`blog/static/blog/css/user.css` 应用为页面背景——所以每个人看到的是自己的背景。

**限制**：头像 ≤ 5 MB，背景图 ≤ 10 MB，支持 jpg / png / gif / webp / bmp。
重新上传会自动删除旧文件（`BlogUser.save()` 里处理），`uploads/` 已在 `.gitignore` 中忽略。

**调整背景的可见程度**：`user.css` 中这一层半透明底色用于保证背景图上的正文可读，

```css
body[data-user-background] #main { background-color: rgb(var(--background) / 0.6); }
```

数值越小背景图越明显；整条删掉则背景完全裸露。

### 9.5 后台界面主题

后台不是 Django 默认的蓝灰配色，而是**与前台共用同一套设计系统**（配色、字体、圆角、
阴影均取自 `frontend/src/styles/main.css`），并支持浅色 / 深色 / 跟随系统三种模式。

实现位于两处，互不干扰：

| 文件 | 作用 |
| --- | --- |
| `templates/admin/base_site.html` | 后台品牌区（站点名 + 「返回前台」入口）与主题样式引入 |
| `blog/static/platform_admin/css/admin.css` | 覆盖 Django admin 的 CSS 自定义属性并微调结构 |

两点维护须知：

1. **Django 的 CSS 变量是颜色，不是 RGB 三元组。** Django 内部会直接写
   `color: var(--body-quiet-color)`，所以赋给 `--body-*`、`--border-*` 这些必须用
   `rgb(...)` 完整颜色值；只有本主题自己的 `--pa-*` 变量才用三元组（配合
   `rgb(var(--pa-primary-500) / 0.2)` 这类带透明度的写法）。
2. **浅色令牌写在 `:root, html:root` 上**，而不是只用 `:root`。Django 的 `base.css`
   同样用 `:root` 定义同名变量，仅靠"后加载"在部分情况下会被反超；`html:root`
   把权重提到与深色规则同级，靠书写顺序决定胜负。

Markdown 编辑器（django-mdeditor / editor.md）由 JavaScript 构建 DOM 且自带浅色主题，
其样式表在本主题之后加载，因此相关覆盖统一使用 `!important`。

**关于内容居中**：Django 的 `#container` 原本没有最大宽度，宽屏下后台会铺满窗口。
本主题给它加了 `max-width: 1400px` 并 `margin-inline: auto` 居中。这里有两个容易踩的点：

1. `#content` 处在 `#main → main.content` 这条 flex 链路上，会被收缩成内容宽度
   （实测约 600px），必须显式给 `width/min-width/max-width: 100%` 才能铺满容器；
2. Django 仪表盘用「`#content-main` 浮动占满 + `#content-related` 负边距右移」的写法，
   在居中容器里右栏会溢出到容器外。本主题改用 flex 换行布局：
   `h1` 标题独占一行（`flex: 0 0 100%`），主区自适应、右栏固定 280px。

## 十、部署说明

- **传统部署**：`deploy/entrypoint.sh` + Nginx 配置见 `deploy/nginx.conf`
- **Docker 部署**：`deploy/docker-compose/docker-compose.yml`
- **Kubernetes 部署**：`deploy/k8s/` 下的 ConfigMap 与 Deployment 清单

生产环境请务必通过环境变量覆盖数据库密码、`DJANGO_SECRET_KEY`，并将 `DJANGO_DEBUG`
设为 `False`。

## 十一、常见问题

**Q：启动时报数据库连接失败？**
检查 MySQL 服务是否已启动、`teaching_resource` 数据库是否已创建，以及 `settings.py`
中的用户名密码是否正确。

**Q：页面样式丢失？**
前端资源需要通过 Vite 构建：进入 `frontend` 目录执行 `npm install && npm run build`，
随后回到项目根目录执行 `python manage.py collectstatic --noinput`。

**Q：切到浅色模式后背景变白了，但卡片/内容块还是黑的？**
这是主题标记 `<html>` 与 `<body>` 不同步导致的。深色令牌的 CSS 规则是
`.dark, [data-theme=dark]`，而 `data-theme` 会被同时写在 `<html>` 和 `<body>` 上；
只要有一处没跟着切换，`<body>` 上的规则就会把深色变量重新套用到所有子元素。
`templates/share_layout/base.html` 的内联脚本与 `frontend/src/features/darkMode.js`
现在都会同步这两处，改主题相关代码时请保持两边一致。

**Q：登录时提示「CSRF 验证失败 / CSRF token from POST incorrect」？**
这是表单校验令牌过期，不是账号问题。Django 在**登录成功和登出时会轮换 CSRF token**，
所以「登录前就已渲染的那张登录表单」（停在旧标签页、或用浏览器后退回到的页面）再提交就会失败。
处理办法：在登录页按 `Ctrl + F5` 强制刷新后重新登录，或清除该站点 Cookie / 用无痕窗口打开。
平台已把这种失败渲染成带「重新登录」按钮的友好页面（见 `CSRF_FAILURE_VIEW`），不会出现 Django 的调试说明页。

若部署到域名后所有表单都报 CSRF 失败，则是 `CSRF_TRUSTED_ORIGINS` 没包含该域名：
把它加进 `.env` 的 `DJANGO_CSRF_TRUSTED_ORIGINS`（逗号分隔）即可。本地开发默认已放行
`http://127.0.0.1:8000` 与 `http://localhost:8000`。

**Q：搜索报错？**
默认使用 Whoosh，索引目录为 `whoosh_index/`。如需重建索引，执行
`python manage.py rebuild_index`（Elasticsearch 模式请先配置 `DJANGO_ELASTICSEARCH_HOST`）。

**Q：改了模板里的 Tailwind 类，样式没生效？**
Tailwind 是按需生成的：模板里新出现的类，必须重新执行 `npm run build` 才会写进 CSS，
否则该类在样式表中不存在（例如 `hidden` 与 `lg:inline-flex` 同时使用时，
若 `lg:inline-flex` 未生成，元素会被一直隐藏）。

**Q：改了 HTML 模板，刷新页面没变化？**
Django 5.2 起模板加载器固定使用 `cached.Loader`，模板只在进程启动时读取一次。
用 `start.bat`（即 `runserver` 不带 `--noreload`）启动时，自动重载器会在模板变更后
重启服务，无需手动干预；若用 `--noreload` 启动，改完模板需要手动重启服务。

**Q：`text-primary`、`bg-primary/5` 这类类没有效果？**
本项目主题色 `primary` 在 `tailwind.config.js` 中只定义了 `50~900` 色阶，没有 `DEFAULT`，
所以要使用带色阶的写法，如 `text-primary-500`、`bg-primary-500/10`、`border-primary-500/40`。

---

## 许可证

本项目基于 [MIT License](LICENSE) 发布。
