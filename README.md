# 简易用户信息管理平台

> 基于 Python Flask 构建的用户登录与信息展示系统，已进行全面的安全加固。

---

## 📋 项目概述

一个轻量级的用户信息管理平台，提供用户登录/登出、信息展示等基础功能。项目以安全实战为目的，展示了从"存在多个高危漏洞的代码"到"生产级安全加固"的完整修复过程。

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
|----------|------|------|
| `SECRET_KEY` | ✅ | Flask 应用密钥，用于 session 签名，请使用强随机字符串 |
| `ADMIN_PWD` | ✅ | 管理员 `admin` 的登录密码 |
| `ALICE_PWD` | ✅ | 普通用户 `alice` 的登录密码 |
| `FLASK_DEBUG` | ❌ | 设为 `true` 开启 debug 模式（仅开发环境） |
| `ENABLE_HTTPS` | ❌ | 设为 `true` 启用 Secure Cookie（仅 HTTPS 环境） |

> **提示：** 参考 `.env.example` 文件了解所有可配置项。

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
| 健康检查 | http://localhost:5000/health |

---

## 👤 测试账号

| 用户名 | 密码 | 角色 | 余额 |
|--------|------|------|------|
| `admin` | `admin123` | 管理员 | 99999 |
| `alice` | `alice2025` | 普通用户 | 100 |

---

## 📁 项目结构

```
/opt/Class01/
├── app.py                     # Flask 主应用（安全加固版）
├── .env.example               # 环境变量配置示例
├── README.md                  # 项目说明文档（本文件）
├── static/
│   └── css/
│       └── style.css          # 全局样式文件
└── templates/
    ├── base.html              # 基础模板（导航栏 + 布局 + CSRF 保护）
    ├── login.html             # 登录页面
    ├── index.html             # 首页（用户信息展示 / 未登录提示）
    ├── 403.html               # 自定义禁止访问页面
    ├── 404.html               # 自定义页面未找到
    └── 500.html               # 自定义服务器错误页面
```

---

## 🛡️ 安全加固功能

本项目在生产环境中已启用以下安全措施：

| 安全功能 | 说明 |
|---------|------|
| 🔑 **凭据不硬编码** | 所有密码和密钥通过环境变量注入，代码零敏感信息 |
| 🔐 **bcrypt 密码哈希** | 存储时加盐哈希，比对使用 `checkpw`，防拖库泄露 |
| 🚫 **安全视图模型** | 仅返回展示必需的字段，过滤 password/phone/email |
| 💢 **CSRF 防护** | Double Submit Cookie 模式，所有 POST 表单携带 token |
| 🍪 **Session 加固** | 30 分钟过期、HttpOnly、SameSite=Lax、支持 Secure |
| 🛡️ **HTTP 安全头** | Content-Security-Policy、X-Frame-Options、X-Content-Type-Options 等 7 项 |
| 🔇 **Debug 模式可控** | 环境变量控制，生产环境默认关闭 |
| 🔍 **输入校验** | 前后端双重校验：长度限制 + 字符白名单 |
| ⏱️ **登录频率限制** | 5 次失败 / 15 分钟窗口，超限封禁 15 分钟 |
| 📝 **安全日志审计** | JSON 格式记录登录/登出/CSRF/频率限制等事件 |
| ✅ **环境变量校验** | 启动时检查必需变量，缺失即报错退出 |
| 🚪 **登出 CSRF 防护** | 仅接受 POST 请求，需携带有效 CSRF token |
| ❌ **自定义错误页** | 404/403/500 友好页面，不泄露框架信息 |

---

## 🌐 API 接口

| 路由 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 首页，已登录显示用户信息，未登录提示登录 |
| `/login` | GET/POST | 登录页面。POST 需携带 `username`、`password`、`_csrf_token` |
| `/logout` | POST | 登出（需携带 `_csrf_token`） |
| `/logout_get` | GET | GET 方式登出（向后兼容，会记录安全告警日志） |
| `/health` | GET | 健康检查，返回 `{"status": "ok"}` |

---

## 🧪 功能测试

```bash
# 1. 访问首页
curl http://localhost:5000/

# 2. 访问登录页
curl http://localhost:5000/login

# 3. 获取 CSRF token 并登录
# 先获取登录页提取 CSRF token
PAGE=$(curl -s -c cookies.txt http://localhost:5000/login)
CSRF=$(echo "$PAGE" | grep -oP 'value="\K[a-f0-9]{64}(?=")' | head -1)

# 提交登录
curl -s -b cookies.txt -c cookies.txt \
    -d "username=admin&password=admin123&_csrf_token=$CSRF" \
    -X POST http://localhost:5000/login

# 4. 使用首页的 CSRF token 登出
HOME=$(curl -s -b cookies.txt http://localhost:5000/)
CSRF_LOGOUT=$(echo "$HOME" | grep -oP 'value="\K[a-f0-9]{64}(?=")' | head -1)
curl -s -b cookies.txt -d "_csrf_token=$CSRF_LOGOUT" \
    -X POST http://localhost:5000/logout

# 5. 健康检查
curl http://localhost:5000/health
```

---

## 🎨 技术栈

| 技术 | 用途 |
|------|------|
| [Python Flask](https://flask.palletsprojects.com/) | Web 框架 |
| [Jinja2](https://jinja.palletsprojects.com/) | 模板引擎 |
| [bcrypt](https://pypi.org/project/bcrypt/) | 密码哈希 |
| HTML5 + CSS3 | 前端界面 |

---

## 📊 设计要点

### 前端界面

- **蓝色渐变导航栏**（`#667eea` → `#764ba2`），flex 布局
- **卡片式布局**：白色背景、圆角边框、柔和阴影
- **登录页**：聚焦的输入框、表单校验、错误提示
- **首页**：用户信息列表展示、退出按钮
- **错误页**：统一风格，大号状态码 + 友好提示 + 返回首页按钮

### 安全架构

- **配置分离**：所有凭据通过环境变量注入
- **纵深防御**：CSRF + Session 加固 + HTTP 安全头 + 输入校验 + 频率限制
- **日志审计**：JSON 格式结构化日志，支持导入 SIEM 系统

---

## ⚠️ 已知限制

- 用户数据硬编码在代码中（内存存储），重启后丢失
- 无注册功能（仅内置 admin 和 alice 两个账号）
- 登录频率限制基于内存（进程重启后重置）
- 无 RBAC 权限控制（角色字段预留但未实现权限逻辑）

---

## 📝 安全文档

详细的漏洞修复过程参见项目根目录的 `综合安全漏洞修复报告.md`，涵盖全部 14 项漏洞的：

- 原始问题与攻击场景
- 修复方案与代码对比
- 验证结果与测试矩阵

---

## 📄 许可证

本项目仅用于学习与安全演示目的。

---

*项目生成于 2026-07-19 | Python Flask + bcrypt | 安全加固版 v2.0*
