# 简易用户信息管理平台

> 基于 Python Flask 构建的用户管理系统，支持登录、注册、搜索、头像上传功能，已完成 **24 项**安全漏洞修复。

---

## 📋 项目概述

一个轻量级的用户信息管理平台，提供用户登录/注册、信息展示、用户搜索、头像上传等完整功能。项目以安全实战为目的，经过多轮安全加固，从"存在多个高危漏洞的代码"演进为"生产级安全防护"的完整示例。

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip (Python 包管理器)

### 安装依赖

```bash
pip install flask bcrypt
```

### 配置环境变量

项目使用环境变量管理所有敏感信息，启动前必须设置：

```bash
export SECRET_KEY="your-strong-secret-key-at-least-32-chars"
export ADMIN_PWD="admin123"
export ALICE_PWD="alice2025"
```

| 环境变量 | 必需 | 说明 |
|----------|:----:|------|
| `SECRET_KEY` | ✅ | Flask 应用密钥，用于 session 签名，请使用强随机字符串 |
| `ADMIN_PWD` | ✅ | 管理员 `admin` 的登录密码 |
| `ALICE_PWD` | ✅ | 普通用户 `alice` 的登录密码 |
| `FLASK_DEBUG` | ❌ | 设为 `true` 开启 debug 模式（仅开发环境） |
| `ENABLE_HTTPS` | ❌ | 设为 `true` 启用 Secure Cookie（仅 HTTPS 环境） |

> 参考 `.env.example` 文件了解所有可配置项。

### 启动服务

```bash
cd /opt/Class01
python app.py
```

启动输出示例：

```
[启动] 用户管理平台 v2.0 (安全加固版)
[启动] Debug 模式: 关闭
[启动] Session 过期时间: 30 分钟
[启动] 登录频率限制: 5 次 / 15 分钟
[启动] HTTP 安全头: 已启用
[启动] CSRF 保护: 已启用
[启动] 安全日志: /var/log/class01/security.log
```

### 访问服务

| 页面 | 地址 |
|------|------|
| 首页 | http://localhost:5000 |
| 登录页 | http://localhost:5000/login |
| 注册页 | http://localhost:5000/register |
| 头像上传 | http://localhost:5000/upload |
| 健康检查 | http://localhost:5000/health |

---

## 👤 测试账号

| 用户名 | 密码 | 角色 | 余额 |
|--------|:----:|:----:|:----:|
| `admin` | `admin123` | 管理员 | 99999 |
| `alice` | `alice2025` | 普通用户 | 100 |

---

## 📁 项目结构

```
/opt/Class01/
├── 📄 app.py                         # Flask 主应用（全部路由 + 安全加固）
├── 📄 .env.example                   # 环境变量配置示例
├── 📄 README.md                      # 项目说明文档（本文件）
│
├── 📁 data/
│   └── 📄 users.db                   # SQLite 数据库（users表 + uploads表）
│
├── 📁 static/
│   ├── 📁 css/
│   │   └── 📄 style.css              # 全局样式
│   └── 📁 uploads/                   # 用户头像存储目录
│
├── 📁 templates/
│   ├── 📄 base.html                  # 基础模板（导航栏）
│   ├── 📄 index.html                 # 首页（用户信息 + 搜索 + 上传入口）
│   ├── 📄 login.html                 # 登录页
│   ├── 📄 register.html              # 注册页
│   ├── 📄 upload.html                # 头像上传页
│   ├── 📄 403.html                   # 自定义禁止访问页
│   ├── 📄 404.html                   # 自定义页面未找到
│   └── 📄 500.html                   # 自定义服务器错误页
│
├── 📄 综合安全漏洞修复报告.md          # 14项基础安全漏洞修复报告
├── 📄 SQL注入漏洞修复报告.md          # SQL 注入修复报告
└── 📄 文件上传漏洞修复报告.md          # 文件上传漏洞修复报告
```

---

## 🛡️ 安全加固功能（共 24 项修复）

### 第一轮 — 基础安全加固（14 项）

| 安全功能 | 说明 |
|---------|------|
| 🔑 **凭据不硬编码** | 所有密码和密钥通过环境变量注入，代码零敏感信息 |
| 🔐 **bcrypt 密码哈希** | 存储时加盐哈希，比对使用 `checkpw`，防拖库泄露 |
| 🚫 **安全视图模型** | 仅返回展示必需的字段，过滤 password/phone/email |
| 💢 **CSRF 防护** | Double Submit Cookie 模式，所有 POST 表单携带 token |
| 🍪 **Session 加固** | 30 分钟过期、HttpOnly、SameSite=Lax、支持 Secure |
| 🛡️ **HTTP 安全头** | CSP、X-Frame-Options、X-Content-Type-Options 等 7 项 |
| 🔇 **Debug 模式可控** | 环境变量控制，生产环境默认关闭 |
| 🔍 **输入校验** | 前后端双重校验：长度限制 + 字符白名单 |
| ⏱️ **登录频率限制** | 5 次失败 / 15 分钟窗口，超限封禁 15 分钟 |
| 📝 **安全日志审计** | JSON 格式记录登录/登出/CSRF/频率限制等事件 |
| ✅ **环境变量校验** | 启动时检查必需变量，缺失即报错退出 |
| 🚪 **登出 CSRF 防护** | 仅接受 POST 请求，需携带有效 CSRF token |
| ❌ **自定义错误页** | 404/403/500 友好页面，不泄露框架信息 |
| 🔗 **全局 CSRF 注入** | `@app.context_processor` 所有模板自动注入 CSRF token |

### 第二轮 — SQL 注入修复（3 项）

| 安全功能 | 说明 |
|---------|------|
| 🗃️ **参数化查询** | 首页搜索 `LIKE ?` 替代 f-string 拼接 |
| 🗃️ **参数化查询** | `/search` 路由 `LIKE ?` 替代 f-string 拼接 |
| 🗃️ **参数化查询** | 注册接口 `VALUES (?, ?, ?, ?)` 替代 f-string 拼接 |

### 第三轮 — 文件上传修复（7 项）

| 安全功能 | 说明 |
|---------|------|
| 🖼️ **扩展名白名单** | 仅允许 png/jpg/jpeg/gif/webp，拒绝 php/html |
| 🛡️ **存储型 XSS 防御** | 禁止 HTML/JS 文件上传，从源头阻断 XSS |
| 📁 **路径穿越防御** | `os.path.basename()` 剥离所有目录路径 |
| 🔄 **重名检测** | UUID 后缀自动重命名，防止文件覆盖 |
| ✏️ **文件名净化** | 危险字符替换为 `_`，防止日志注入 |
| 👤 **文件关联用户** | `uploads` 数据库表记录上传者、时间、文件名 |
| 📏 **双重大小校验** | Flask 框架层 + 应用层手动检查 Content-Length |

---

## 🌐 API 接口

| 路由 | 方法 | 说明 | 需登录 |
|------|:----:|------|:------:|
| `/` | GET | 首页，已登录显示用户信息，未登录提示登录 | ❌ |
| `/login` | GET/POST | 登录，POST 需 `username` + `password` + `_csrf_token` | ❌ |
| `/register` | GET/POST | 注册新用户，POST 需 `username` + `password` + `_csrf_token` | ❌ |
| `/logout` | POST | 登出（仅 POST 方式，需 `_csrf_token`） | ✅ |
| `/logout_get` | GET | GET 方式登出（向后兼容，记录安全告警日志） | ✅ |
| `/search` | GET | 搜索用户，参数 `?keyword=` | ❌（推荐登录后使用） |
| `/upload` | GET/POST | 头像上传，POST 需 `file` + `_csrf_token` | ✅ |
| `/health` | GET | 健康检查，返回 `{"status":"ok"}` | ❌ |

---

## 🧪 功能测试

### 基础流程测试

```bash
# 1. 访问首页
curl http://localhost:5000/

# 2. 访问登录页
curl http://localhost:5000/login

# 3. 登录
PAGE=$(curl -s -c cookies.txt http://localhost:5000/login)
CSRF=$(echo "$PAGE" | grep -oP 'value="\K[a-f0-9]{64}(?=")' | head -1)
curl -s -b cookies.txt -c cookies.txt \
    -d "username=admin&password=admin123&_csrf_token=$CSRF" \
    -X POST http://localhost:5000/login

# 4. 登出（POST 方式，需从首页获取 CSRF token）
HOME=$(curl -s -b cookies.txt http://localhost:5000/)
CSRF_LOGOUT=$(echo "$HOME" | grep -oP 'value="\K[a-f0-9]{64}(?=")' | head -1)
curl -s -b cookies.txt -d "_csrf_token=$CSRF_LOGOUT" \
    -X POST http://localhost:5000/logout
```

### 注册与搜索测试

```bash
# 1. 注册新用户
PAGE=$(curl -s -c reg.txt http://localhost:5000/register)
CSRF=$(echo "$PAGE" | grep -oP 'value="\K[a-f0-9]{64}(?=")' | head -1)
curl -s -b reg.txt \
    -d "username=newuser&password=new123&email=new@test.com&phone=12345678901&_csrf_token=$CSRF" \
    -X POST http://localhost:5000/register

# 2. 用新用户登录并搜索
PAGE=$(curl -s -c search.txt http://localhost:5000/login)
CSRF=$(echo "$PAGE" | grep -oP 'value="\K[a-f0-9]{64}(?=")' | head -1)
curl -s -b search.txt -c search.txt \
    -d "username=newuser&password=new123&_csrf_token=$CSRF" \
    -X POST http://localhost:5000/login > /dev/null

# 3. 搜索用户
curl -s -b search.txt "http://localhost:5000/search?keyword=admin"

# 4. 健康检查
curl http://localhost:5000/health
```

### 头像上传测试

```bash
# 1. 登录后获取上传页 CSRF
PAGE=$(curl -s -c up.txt http://localhost:5000/login)
CSRF=$(echo "$PAGE" | grep -oP 'value="\K[a-f0-9]{64}(?=")' | head -1)
curl -s -b up.txt -c up.txt \
    -d "username=admin&password=admin123&_csrf_token=$CSRF" \
    -X POST http://localhost:5000/login > /dev/null

# 2. 获取上传页 CSRF token
UP=$(curl -s -b up.txt http://localhost:5000/upload)
CSRF_UP=$(echo "$UP" | grep -oP 'value="\K[a-f0-9]{64}(?=")' | head -1)

# 3. 上传图片
curl -s -b up.txt \
    -F "file=@avatar.png" \
    -F "_csrf_token=$CSRF_UP" \
    -X POST http://localhost:5000/upload
```

---

## 🎨 技术栈

| 技术 | 用途 |
|------|------|
| [Python Flask](https://flask.palletsprojects.com/) | Web 框架 |
| [Jinja2](https://jinja.palletsprojects.com/) | 模板引擎 |
| [SQLite](https://sqlite.org/) | 数据库 |
| [bcrypt](https://pypi.org/project/bcrypt/) | 密码哈希 |
| HTML5 + CSS3 | 前端界面 |

---

## 📊 设计要点

### 前端界面

- **蓝色渐变导航栏**（`#667eea` → `#764ba2`），flex 布局
- **卡片式布局**：白色背景、圆角边框、柔和阴影
- **登录/注册页**：聚焦的输入框、后端校验、错误/成功提示
- **首页**：用户信息展示、搜索表格、上传入口
- **上传页**：图片预览、文件链接展示
- **错误页**：统一风格，大号状态码 + 友好提示 + 返回首页按钮

### 安全架构

- **纵深防御**：7 层 HTTP 安全头 + CSP + CSRF Token + Session 加固 + 输入校验 + 频率限制
- **配置分离**：所有凭据通过环境变量注入
- **参数化查询**：全部 3 处 SQL 语句使用 `?` 占位符，消除 SQL 注入
- **文件上传安全**：扩展名白名单 + 路径穿越防御 + 重名检测 + 文件名净化 + 审计日志
- **日志审计**：JSON 格式结构化日志，记录所有安全事件

---

## ⚠️ 已知限制

- 登录验证使用内存字典 `USERS`（bcrypt 哈希），注册用户写入 SQLite 但登录时未查询 SQLite
- 登录频率限制基于进程内存（重启后重置）
- 文件上传成功后无删除/管理界面
- 无 RBAC 权限控制（角色字段预留但未实现权限逻辑）
- `uploads` 表记录的文件磁盘清理需手动处理

---

## 📝 安全文档

项目根目录包含以下安全报告文件：

| 报告 | 内容 | 漏洞数 |
|------|------|:------:|
| `综合安全漏洞修复报告.md` | 硬编码凭据、明文密码、CSRF、Session、HTTP 头等 | 14 项 |
| `SQL注入漏洞修复报告.md` | 首页搜索注入、搜索路由注入、注册接口注入 | 3 项 |
| `文件上传漏洞修复报告.md` | 任意文件上传、XSS、路径穿越、文件覆盖等 | 7 项 |

**共修复安全漏洞：24 项**

---

*项目生成于 2026-07-21 | Python Flask + SQLite + bcrypt | 安全加固版 v3.0*
