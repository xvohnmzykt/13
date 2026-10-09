from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from blog.models import Article, Tag, Category

CATEGORIES = [
    ('计算机基础', None),
    ('操作系统原理', '计算机基础'),
    ('程序设计', None),
    ('Python 程序设计', '程序设计'),
    ('Java 程序设计', '程序设计'),
    ('数据结构与算法', None),
    ('线性表与树', '数据结构与算法'),
    ('数据库技术', None),
    ('MySQL 数据库应用', '数据库技术'),
]

TAGS = ['课件', '讲义', '实验指导', '习题答案', '教学视频', '课程设计', 'Python', 'MySQL']

RESOURCES = [
    ('数据结构与算法', '线性表与树',
     '《数据结构》第三章 线性表与树 教学课件',
     ['课件', '讲义'],
     """## 本章学习目标

1. 掌握线性表的顺序存储与链式存储结构；
2. 理解二叉树的性质、遍历方式与存储结构；
3. 能够使用递归与非递归两种方式实现二叉树的先序、中序、后序遍历。

## 一、线性表

线性表是最基本、最常用的一种数据结构。它的特点是数据元素之间存在一对一的线性关系。

### 1.1 顺序存储结构

顺序表使用一段地址连续的存储单元依次存储线性表的数据元素，支持随机访问，按下标访问的
时间复杂度为 `O(1)`，但插入和删除需要移动元素，平均时间复杂度为 `O(n)`。

### 1.2 链式存储结构

单链表通过指针把一组任意的存储单元串联起来。插入与删除只需修改指针，时间复杂度为 `O(1)`，
但查找需要从头结点开始顺序遍历。

## 二、树与二叉树

二叉树是每个结点至多有两棵子树的树结构，具有以下重要性质：

- 第 `i` 层至多有 `2^(i-1)` 个结点；
- 深度为 `k` 的二叉树至多有 `2^k - 1` 个结点；
- 对任何一棵二叉树，若叶子结点数为 `n0`，度为 2 的结点数为 `n2`，则 `n0 = n2 + 1`。

## 三、课后练习

请完成教材第 78 页习题 3-1 至 3-8，并提交实验报告。"""),

    ('数据库技术', 'MySQL 数据库应用',
     'MySQL 数据库应用 实验指导书（含完整 SQL 示例）',
     ['实验指导', 'MySQL'],
     """## 实验目的

熟悉 MySQL 的安装配置、库表设计与常用 SQL 语句，能够独立完成一个小型业务数据库的设计。

## 实验环境

- MySQL 8.0
- 字符集：`utf8mb4`
- 客户端：命令行或 MySQL Workbench

## 实验内容

### 1. 创建数据库与数据表

```sql
CREATE DATABASE teaching_resource
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE teaching_resource;

CREATE TABLE course (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    credit      DECIMAL(3,1) DEFAULT 2.0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 2. 数据查询

```sql
-- 查询学分大于 2 的课程，按学分降序排列
SELECT name, credit
FROM course
WHERE credit > 2
ORDER BY credit DESC;
```

### 3. 索引与优化

为经常出现在 `WHERE` 条件中的列建立索引，并使用 `EXPLAIN` 查看执行计划：

```sql
CREATE INDEX idx_course_credit ON course(credit);
EXPLAIN SELECT * FROM course WHERE credit > 2;
```

## 实验要求

1. 独立完成上述 SQL 并截图保存执行结果；
2. 设计一个包含三张以上数据表的教务管理数据库；
3. 撰写实验报告，说明表结构设计思路与索引优化过程。"""),

    ('程序设计', 'Python 程序设计',
     'Python 程序设计 期末复习提纲与习题答案',
     ['习题答案', '讲义'],
     """## 一、基础语法

- 变量与数据类型：`int`、`float`、`str`、`bool`、`list`、`tuple`、`dict`、`set`
- 流程控制：`if / elif / else`、`for`、`while`、`break`、`continue`
- 函数：位置参数、关键字参数、默认参数、可变参数 `*args` / `**kwargs`

## 二、面向对象

```python
class Course:
    \"\"\"课程类：封装课程名称与学分。\"\"\"

    def __init__(self, name: str, credit: float = 2.0):
        self.name = name
        self.credit = credit

    def __str__(self) -> str:
        return f'{self.name}（{self.credit} 学分）'


if __name__ == '__main__':
    print(Course('数据结构', 4.0))
```

## 三、典型习题

**题目 1**：统计一段文本中每个单词出现的次数，按次数降序输出。

```python
from collections import Counter

text = 'data structure and algorithm'
print(Counter(text.split()).most_common())
```

**题目 2**：编写函数判断一个字符串是否为回文串。

```python
def is_palindrome(s: str) -> bool:
    s = ''.join(ch.lower() for ch in s if ch.isalnum())
    return s == s[::-1]
```

## 四、复习建议

重点掌握列表推导式、生成器、异常处理与文件读写，期末考试中编程题占比约 40%。"""),

    ('计算机基础', '操作系统原理',
     '操作系统原理 第五章 进程同步与互斥 教学课件',
     ['课件', '教学视频'],
     """## 本章重点

1. 进程同步与互斥的基本概念；
2. 临界区与临界资源；
3. 信号量机制与 P、V 操作；
4. 经典同步问题：生产者—消费者、读者—写者、哲学家进餐。

## 一、临界区

多个进程并发访问同一共享资源时，该资源称为**临界资源**，访问临界资源的那段代码称为
**临界区**。为保证正确性，临界区的使用必须满足：

- **空闲让进**：临界区空闲时应允许一个进程立即进入；
- **忙则等待**：已有进程在临界区内时，其他进程必须等待；
- **有限等待**：等待进入临界区的进程应在有限时间内进入；
- **让权等待**：进程不能进入临界区时应释放处理机。

## 二、信号量机制

信号量 `S` 是一个整型变量，仅能通过两个原子操作访问：

```
P(S):  S = S - 1;  if (S < 0) block();
V(S):  S = S + 1;  if (S <= 0) wakeup();
```

## 三、生产者—消费者问题

```c
semaphore mutex = 1;   // 互斥访问缓冲区
semaphore empty = n;   // 空闲缓冲区数量
semaphore full  = 0;   // 已存放产品数量

// 生产者
P(empty); P(mutex);
put_item();
V(mutex); V(full);

// 消费者
P(full); P(mutex);
get_item();
V(mutex); V(empty);
```

## 四、思考题

为什么生产者进程中 `P(empty)` 必须写在 `P(mutex)` 之前？请结合死锁产生的条件说明原因。"""),

    ('程序设计', 'Java 程序设计',
     'Java 程序设计 课程设计任务书',
     ['课程设计', '讲义'],
     """## 一、设计题目

学生信息管理系统（控制台版或 Swing 图形界面版均可）。

## 二、功能要求

1. 学生信息的添加、删除、修改与查询；
2. 按学号、姓名、班级进行模糊查询；
3. 学生成绩的录入与统计（平均分、最高分、及格率）；
4. 数据持久化：使用文件或 JDBC + MySQL 保存数据；
5. 异常处理：对非法输入给出友好提示。

## 三、技术要求

- 使用面向对象思想设计，至少包含 3 个以上实体类；
- 使用集合框架（`ArrayList` / `HashMap`）组织数据；
- 代码需有完整注释，命名符合 Java 规范；
- 提交内容包括源代码、设计文档与答辩 PPT。

## 四、进度安排

| 周次 | 任务 |
| --- | --- |
| 第 1 周 | 需求分析与总体设计 |
| 第 2—3 周 | 编码实现 |
| 第 4 周 | 测试与文档撰写 |
| 第 5 周 | 验收答辩 |

## 五、评分标准

功能完整性 40%，代码规范性 25%，文档质量 20%，答辩表现 15%。"""),
]


class Command(BaseCommand):
    help = '创建教学资源平台演示数据（分类、标签、教学资源）'

    def handle(self, *args, **options):
        user_model = get_user_model()
        user = user_model.objects.get_or_create(
            email='teacher@example.com',
            username='teacher',
            defaults={'password': make_password('teacher@2026'), 'nickname': '教务管理员'},
        )[0]

        category_map = {}
        for name, parent_name in CATEGORIES:
            parent = category_map.get(parent_name) if parent_name else None
            category, _ = Category.objects.get_or_create(name=name, parent_category=parent)
            category_map[name] = category

        top_level = [n for n, p in CATEGORIES if p is None]
        child_level = [n for n, p in CATEGORIES if p is not None]

        tag_objects = {}
        for tag_name in TAGS:
            tag_objects[tag_name] = Tag.objects.get_or_create(name=tag_name)[0]

        created = 0
        for _parent_name, child_name, title, tag_names, body in RESOURCES:
            article, is_new = Article.objects.get_or_create(
                title=title,
                defaults={
                    'body': body,
                    'author': user,
                    'category': category_map[child_name],
                    'type': 'a',
                    'status': 'p',
                    'comment_status': 'o',
                },
            )
            if is_new:
                created += 1
            for tag_name in tag_names:
                tag = tag_objects.get(tag_name) or Tag.objects.get_or_create(name=tag_name)[0]
                article.tags.add(tag)

        from teachingplatform.utils import cache
        cache.clear()
        self.stdout.write(self.style.SUCCESS(
            f'演示数据创建完成：{len(top_level)} 个一级分类、'
            f'{len(child_level)} 个二级分类、{len(TAGS)} 个标签、'
            f'{created} 条新教学资源。'))
        self.stdout.write('演示账号：teacher / teacher@2026')
