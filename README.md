# 简易用户信息管理平台

> 基于 Python Flask 构建的用户管理系统，支持登录、注册、搜索、头像上传、个人中心、充值、帮助中心功能，已完成 **34 项**安全漏洞修复。

---

## 📋 项目概述

一个轻量级的用户信息管理平台，提供用户登录/注册、信息展示、用户搜索、头像上传、个人中心、余额充值、动态帮助中心等完整功能。项目以安全实战为目的，经过多轮安全加固，从"存在多个高危漏洞的代码"演进为"生产级安全防护"的完整示例。

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
[启动] 用户管理平台 v3.0 (安全加固版)
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
| 个人中心 | http://localhost:5000/profile?user_id=1 |
| 帮助中心 | http://localhost:5000/page?name=help |
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
├── 📁 pages/
│   └── 📄 help.html                  # 帮助中心页面
│
├── 📁 static/
│   ├── 📁 css/
│   │   └── 📄 style.css              # 全局样式
│   └── 📁 uploads/                   # 用户头像存储目录
│
├── 📁 templates/
│   ├── 📄 base.html                  # 基础模板（导航栏）
│   ├── 📄 index.html                 # 首页（用户信息 + 搜索 + 快捷入口 + 动态页面）
│   ├── 📄 login.html                 # 登录页
│   ├── 📄 register.html              # 注册页
│   ├── 📄 profile.html               # 个人中心（信息展示 + 充值）
│   ├── 📄 upload.html                # 头像上传页
│   ├── 📄 403.html                   # 自定义禁止访问页
│   ├── 📄 404.html                   # 自定义页面未找到
│   └── 📄 500.html                   # 自定义服务器错误页
│
├── 📄 综合安全漏洞修复报告.md          # 14项基础安全漏洞修复报告
├── 📄 SQL注入漏洞修复报告.md          # SQL 注入修复报告（3 项）
├── 📄 文件上传漏洞修复报告.md          # 文件上传漏洞修复报告（7 项）
├── 📄 充值功能与个人中心漏洞修复报告.md  # 充值/个人中心修复报告（8 项）
└── 📄 动态页面加载功能漏洞修复报告.md    # 动态页面加载修复报告（2 项）
```

---

## 🛡️ 安全加固功能（共 34 项修复）

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

### 第四轮 — 充值/个人中心修复（8 项）

| 安全功能 | 说明 |
|---------|------|
| 👤 **充值身份校验** | 只能给自己充值，拦截跨用户操作 |
| ✅ **金额正负校验** | 禁止负数充值，防止余额盗取 |
| 🔝 **金额上限校验** | 单次充值不超过 100,000 |
| 💢 **充值 CSRF 校验** | 充值接口增加 CSRF token 验证 |
| 🔢 **金额类型校验** | 拒绝浮点数和字符串，仅接受整数 |
| 🔒 **个人中心登录限制** | 未登录不可查看个人资料 |
| 🙈 **敏感信息脱敏** | 非本人查看时隐藏 email 和 phone |
| 📋 **充值审计日志** | 每次充值记录金额、操作者、目标用户 |

### 第五轮 — 动态页面加载修复（2 项）

| 安全功能 | 说明 |
|---------|------|
| 🛡️ **LFI 路径穿越防御** | `os.path.realpath()` + `startswith` 前缀校验拦截 `../` |
| 🔒 **页面加载登录限制** | 未登录不可访问 `/page` 路由 |

---

## 🌐 API 接口

| 路由 | 方法 | 说明 | 需登录 |
|------|:----:|------|:------:|
| `/` | GET | 首页，已登录显示用户信息，未登录提示登录 | ❌ |
| `/login` | GET/POST | 登录，POST 需 `username` + `password` + `_csrf_token` | ❌ |
| `/register` | GET/POST | 注册新用户，POST 需 `username` + `password` + `_csrf_token` | ❌ |
| `/logout` | POST | 登出（仅 POST 方式，需 `_csrf_token`） | ✅ |
| `/logout_get` | GET | GET 方式登出（向后兼容，记录安全告警日志） | ✅ |
| `/search` | GET | 搜索用户，参数 `?keyword=` | ❌ |
| `/upload` | GET/POST | 头像上传，POST 需 `file` + `_csrf_token` | ✅ |
| `/profile` | GET | 个人中心，参数 `?user_id=`，本人完整/他人脱敏 | ✅ |
| `/recharge` | POST | 充值，需 `user_id` + `amount` + `_csrf_token`（仅限本人） | ✅ |
| `/page` | GET | 动态页面加载，参数 `?name=`，读取 `pages/` 目录文件 | ✅ |
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

### 动态页面加载测试

```bash
# 1. 登录后访问帮助中心
PAGE=$(curl -s -c pg.txt http://localhost:5000/login)
CSRF=$(echo "$PAGE" | grep -oP 'value="\K[a-f0-9]{64}(?=")' | head -1)
curl -s -b pg.txt -c pg.txt \
    -d "username=admin&password=admin123&_csrf_token=$CSRF" \
    -X POST http://localhost:5000/login > /dev/null

# 2. 加载帮助中心
curl -s -b pg.txt "http://localhost:5000/page?name=help"

# 3. 不存在的页面
curl -s -b pg.txt "http://localhost:5000/page?name=notexist"

# 4. 路径穿越攻击（已被拦截）
curl -s -b pg.txt "http://localhost:5000/page?name=../app.py"
```

### 个人中心与充值测试

```bash
# 1. 登录后查看自己的个人中心
curl -s -b cookies.txt "http://localhost:5000/profile?user_id=1"

# 2. 查看其他用户的个人中心（邮箱/手机脱敏）
curl -s -b cookies.txt "http://localhost:5000/profile?user_id=2"

# 3. 充值（只能给自己充）
PAGE=$(curl -s -b cookies.txt "http://localhost:5000/profile?user_id=1")
CSRF=$(echo "$PAGE" | grep -oP 'value="\K[a-f0-9]{64}(?=")' | head -1)
curl -s -b cookies.txt \
    -d "user_id=1&amount=500&_csrf_token=$CSRF" \
    -X POST http://localhost:5000/recharge
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
- **首页**：用户信息展示、搜索表格、快捷入口（个人中心/上传头像/帮助中心）
- **个人中心**：用户资料展示 + 充值表单，敏感信息条件脱敏
- **动态页面**：`/page?name=help` 加载帮助中心，支持自动 `.html` 后缀补全
- **上传页**：图片预览、文件链接展示
- **错误页**：统一风格，大号状态码 + 友好提示 + 返回首页按钮

### 安全架构

- **纵深防御**：7 层 HTTP 安全头 + CSP + CSRF Token + Session 加固 + 输入校验 + 频率限制
- **配置分离**：所有凭据通过环境变量注入
- **参数化查询**：全部 SQL 语句使用 `?` 占位符，消除 SQL 注入
- **文件上传安全**：扩展名白名单 + 路径穿越防御 + 重名检测 + 文件名净化 + 审计日志
- **充值安全**：身份校验 + CSRF 校验 + 正负校验 + 上限校验 + 类型校验 + 审计日志
- **动态页面安全**：`os.path.realpath()` 路径校验拦截 `../`，登录限制防止未授权访问
- **信息脱敏**：非本人查看个人中心时隐藏 email 和 phone
- **日志审计**：JSON 格式结构化日志，记录所有安全事件

---

## ⚠️ 已知限制

- 登录验证使用内存字典 `USERS`（bcrypt 哈希），注册用户写入 SQLite 但登录时未查询 SQLite，导致注册用户无法登录
- 登录频率限制基于进程内存（重启后重置）
- 文件上传成功后无删除/管理界面
- 个人中心余额对登录用户全部可见（非本人也可查看他人余额）
- 搜索接口未限制登录（未登录可搜索用户信息）
- `/logout_get` GET 方式登出可被 CSRF 利用
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
| `充值功能与个人中心漏洞修复报告.md` | 身份校验、CSRF、金额校验、信息脱敏等 | 8 项 |
| `动态页面加载功能漏洞修复报告.md` | LFI 路径穿越、登录权限缺失 | 2 项 |

**共修复安全漏洞：34 项**

---

## 🔗 功能导航

| 功能 | 入口 | 说明 |
|------|------|------|
| **首页** | `/` | 用户信息 + 搜索 + 快捷入口 |
| **登录** | `/login` | 用户名 + 密码登录 |
| **注册** | `/register` | 新用户注册（写入 SQLite） |
| **个人中心** | `/profile?user_id=` | 查看资料 + 充值（仅本人可见敏感信息） |
| **充值** | `/recharge` | POST 方式充值（仅限本人账户） |
| **帮助中心** | `/page?name=help` | 动态加载帮助中心页面 |
| **头像上传** | `/upload` | 上传头像图片 |
| **用户搜索** | `/search?keyword=` | 搜索用户 |
| **健康检查** | `/health` | 服务状态检查 |

---

*项目更新于 2026-07-22 | Python Flask + SQLite + bcrypt | 安全加固版 v3.0*
