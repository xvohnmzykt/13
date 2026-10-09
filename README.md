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
| 用户模块 | 注册、登录、找回密码、邮箱验证码、个人资料与头像、基于邮箱或用户名的登录 |
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

浏览器访问 <http://127.0.0.1:8000/> 进入平台首页，访问 <http://127.0.0.1:8000/admin/>
进入后台管理。

### 7. 可选：生成演示数据

```bash
python manage.py create_testdata
```

## 九、后台管理

后台地址：`/admin/`，仅超级管理员可登录。主要功能：

- **教学资源**：新增、编辑、批量发布 / 设为草稿、设置置顶排序、开启或关闭评论
- **课程分类 / 标签**：维护多级分类体系与标签库
- **评论**：审核、隐藏、回复
- **平台配置**：平台名称、简介、SEO 关键词、备案号、统计代码、配色方案
- **用户**：创建、禁用、重置密码
- **插件**：查看已加载插件及其元信息

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

**Q：搜索报错？**
默认使用 Whoosh，索引目录为 `whoosh_index/`。如需重建索引，执行
`python manage.py rebuild_index`（Elasticsearch 模式请先配置 `DJANGO_ELASTICSEARCH_HOST`）。

---

## 许可证

本项目基于 [MIT License](LICENSE) 发布。
