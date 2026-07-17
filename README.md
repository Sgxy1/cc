# 后台管理系统

一个基于 Flask 的教学用 Web 应用系统，包含完整的用户管理功能。
本项目用于安全漏洞教学演示，每个功能模块均包含典型的安全漏洞及其修复方案。

## 功能模块

| 天数 | 功能 | 涉及漏洞 |
|:----:|------|----------|
| Day 1 | 用户登录 & 信息展示 | 密码明文存储、调试信息泄露 |
| Day 2 | 用户注册 & 模糊搜索 | SQL 注入（f-string 拼接） |
| Day 3 | 头像上传 | 文件上传无限制、路径穿越 |
| Day 4 | 个人中心 & 充值 | 越权访问（IDOR）、金额篡改、CSRF、用户枚举 |
| Day 5 | 动态页面加载 | 本地文件包含（LFI）、HTML 注入 |
| Day 6 | 密码修改 | CSRF、越权修改密码、无原密码校验 |
| Day 7 | URL 抓取 | SSRF（服务端请求伪造） |
| Day 8 | Ping 网络诊断 | 命令注入（Command Injection） |
| Day 9 | XML 数据导入 | XXE（XML 外部实体注入） |

## 版本演进

```
Day9 修复   --  禁用外部实体声明
Day9 原码   --  XML数据导入功能（XXE漏洞）
Day8 修复   --  危险字符过滤 + 参数列表代替 shell=True
Day8 原码   --  Ping网络诊断功能（命令注入漏洞）
Day7 修复   --  协议限制 + 内网地址拦截
Day7 原码   --  URL抓取功能（SSRF漏洞）
Day6 修复   --  原密码校验 + CSRF Token + Session绑定
Day6 原码   --  密码修改功能（无原密码验证 + 越权修改 + 无CSRF）
Day5 修复   --  路径过滤 + 移除未转义渲染
Day5 原码   --  动态页面加载功能（文件包含漏洞 + HTML注入）
Day4 修复   --  权限校验与金额验证
Day4 原码   --  个人中心与充值功能（IDOR + 金额篡改 + CSRF）
Day3 修复   --  文件上传安全加固
Day3 原码   --  头像上传功能（文件上传漏洞）
Day2 修复   --  参数化查询
Day2 原码   --  注册+搜索功能（SQL注入漏洞）
Day1 修复 2.0 -- bcrypt 安全加固
Day1 原码 2.0 -- 用户登录功能（明文密码漏洞）
Day1 修复 1.0 -- bcrypt + 接口鉴权 + 移除前端硬编码
Day1 原码 1.0 -- MD5 哈希 + 前端硬编码（对应已提交报告）
```

## 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install flask bcrypt
```

### 启动服务

```bash
python app.py
```

服务启动后访问：**http://localhost:5000**

### 测试账号

| 用户名 | 密码 | 角色 | 余额 |
|--------|------|------|------|
| admin | admin123 | 管理员 | 99999 |
| alice | alice2025 | 普通用户 | 100 |

## 项目结构

```
cc/
├── app.py                       # 主应用（所有路由和业务逻辑）
├── requirements.txt             # Python 依赖清单
├── README.md                    # 项目说明文档
│
├── data/
│   └── users.db                 # SQLite 用户数据库（运行时生成）
│
├── templates/                   # Jinja2 模板文件
│   ├── base.html                # 基础模板（导航栏、布局）
│   ├── login.html               # 登录页面
│   ├── index.html               # 首页（用户信息 + 搜索）
│   ├── register.html            # 注册页面
│   ├── upload.html              # 上传页面
│   └── profile.html             # 个人中心页面
│
├── static/
│   └── css/
│       └── style.css            # 全局样式
│
└── uploads/                     # 上传文件存储目录（Day 3 修复后）
```

## 安全漏洞清单

### Day 1：密码安全漏洞

| 漏洞 | 描述 | 代码位置 |
|------|------|----------|
| 明文密码存储 | USERS 字典直接存储明文密码 | app.py 2.0 原码 |
| 密码 == 比对 | 直接用等号比对字符串，无安全哈希 | app.py 2.0 原码 |
| 密码页面泄露 | 登录后将完整用户信息（含密码）传给模板显示 | app.py 2.0 原码 |
| HTML 注释泄露 | login.html 顶部注释暴露默认管理账号 | login.html 2.0 原码 |

**修复方案：** 使用 bcrypt 哈希存储密码，移除页面密码显示，删除调试注释

### Day 2：SQL 注入漏洞

| 漏洞 | 描述 | 代码位置 |
|------|------|----------|
| 注册 SQL 注入 | f-string 拼接 SQL INSERT 语句 | app.py Day2 原码 |
| 搜索 SQL 注入 | f-string 拼接 SQL SELECT 语句 | app.py Day2 原码 |
| SQL 控制台输出 | 执行的 SQL 语句打印到控制台 | app.py Day2 原码 |

**攻击示例：**
```
搜索: keyword=' OR '1'='1           -> 万能查询，返回全部用户
搜索: keyword=' UNION SELECT ...--  -> UNION 注入，窃取额外数据
```

**修复方案：** 使用参数化查询（? 占位符）

### Day 3：文件上传漏洞

| 漏洞 | 描述 | 代码位置 |
|------|------|----------|
| 无文件类型校验 | 不检查扩展名、MIME 类型、文件头 | app.py Day3 原码 /upload |
| 原始文件名保存 | 使用用户上传的原始文件名 | app.py Day3 原码 |
| Web 可访问目录 | 文件保存到 static/uploads/ 可直接 URL 访问 | app.py Day3 原码 |
| 文件大小过大 | MAX_CONTENT_LENGTH 设为 16MB | app.py Day3 原码 |

**修复方案：** 白名单校验 + UUID 重命名 + 非 Web 目录存储 + 2MB 限制

### Day 4：越权访问 & 充值漏洞

| 漏洞 | 描述 | 代码位置 |
|------|------|----------|
| IDOR 越权访问 | /profile 无登录校验，任意 user_id 可查他人资料 | app.py Day4 原码 |
| 任意金额修改 | /recharge 不做 amount 正负检查，可充负数盗钱 | app.py Day4 原码 |
| 隐藏字段篡改 | user_id 来自表单隐藏字段，客户端可随意修改 | profile.html Day4 原码 |
| 无 CSRF 保护 | 充值接口无 CSRF Token，可被跨站请求伪造利用 | app.py Day4 原码 |
| 用户枚举 | 根据返回内容可判断 user_id 是否存在 | app.py Day4 原码 |

**修复方案：** 登录校验 + 会话身份绑定 + amount 正数验证 + CSRF Token

### Day 5：本地文件包含漏洞

| 漏洞 | 描述 | 代码位置 |
|------|------|----------|
| 本地文件包含（LFI） | name 参数未做过滤直接拼接文件路径，可包含任意本地文件 | app.py Day5 原码 /page |
| HTML 注入（XSS） | 模板使用 `| safe` 未转义渲染文件内容，恶意脚本可执行 | templates/index.html Day5 原码 |

**攻击示例：**
```
访问 /page?name=../app.py         -> 包含 app.py 源代码
访问 /page?name=../data/users.db  -> 包含数据库文件
上传 evil.html 后 /page?name=../uploads/evil.html -> XSS
```

**修复方案：** 过滤 `..` `/` `\` 字符 + 移除模板 `| safe` 过滤器

### Day 6：密码修改漏洞

| 漏洞 | 描述 | 代码位置 |
|------|------|----------|
| 无原密码校验 | 修改密码时不需要输入原密码 | app.py Day6 原码 /change-password |
| 越权修改密码 | 已登录用户可修改任何人的密码（隐藏字段） | app.py Day6 原码 |
| 无 CSRF 防护 | 修改密码接口无 CSRF Token | app.py Day6 原码 |

**攻击示例：**
```
POST /change-password username=admin, new_password=hacked123
-> 任意已登录用户可将管理员密码改为 hacked123
-> 攻击者之后用 admin/hacked123 登录，获取管理员权限
```

**修复方案：** 校验原密码 + Session身份绑定 + CSRF Token

### Day 7：SSRF 服务端请求伪造漏洞

| 漏洞 | 描述 | 代码位置 |
|------|------|----------|
| SSRF | 用户可提交任意 URL，服务端直接请求该地址 | app.py Day7 原码 /fetch-url |
| 内网探测 | 未限制目标 IP 范围，可访问内网服务 | app.py Day7 原码 |
| file 协议读取 | 未限制协议，支持 file:// 读取本地文件 | app.py Day7 原码 |

**攻击示例：**
```
POST /fetch-url url=http://127.0.0.1:5000/   -> 访问本机服务
POST /fetch-url url=file:///etc/passwd        -> 读取系统文件
POST /fetch-url url=http://10.0.0.1:3306      -> 探测内网数据库
```

**修复方案：** 限制协议为 http/https + 禁止内网地址

### Day 8：命令注入漏洞

| 漏洞 | 描述 | 代码位置 |
|------|------|----------|
| 命令注入 | f-string 拼接用户输入到系统命令 | app.py Day8 原码 /ping |
| shell=True 执行 | subprocess 启用 shell 解析特殊字符 | app.py Day8 原码 |
| 无输入过滤 | 对 ip 参数未做任何过滤校验 | app.py Day8 原码 |

**攻击示例：**
```
输入 127.0.0.1; whoami      -> 执行系统命令，显示当前用户
输入 127.0.0.1; dir         -> 列出服务器目录
输入 127.0.0.1; cat /etc/passwd -> 读取系统敏感文件
```

**修复方案：** 危险字符黑名单过滤 + 参数列表代替 shell=True

### Day 9：XXE 外部实体注入漏洞

| 漏洞 | 描述 | 代码位置 |
|------|------|----------|
| XXE 注入 | 解析 XML 时加载外部实体，可读取本地文件 | app.py Day9 原码 /xml-import |
| 文件读取 | ENTITY 定义中指定 SYSTEM 文件路径可读取任意文件 | app.py Day9 原码 |

**攻击示例：**
```xml
<!-- 提交以下 XML 数据可读取服务器文件 -->
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>
  <user>
    <name>&xxe;</name>
    <email>test@test.com</email>
  </user>
</root>
```

**修复方案：** 检测并拒绝含有 !ENTITY 或 !DOCTYPE 声明的 XML 数据

## 许可证

本项目仅供教学演示使用，请勿用于实际生产环境。
