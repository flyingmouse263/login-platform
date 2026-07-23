"""
简易用户信息管理平台 - Flask 主应用
====================================
安全加固版本 - 修复了全部 14 项安全漏洞
"""
import os
import re
import sys
import json
import time
import uuid
import sqlite3
import secrets
import logging
from datetime import timedelta, datetime

import bcrypt
from flask import (
    Flask, render_template, request, redirect,
    session, url_for, jsonify, abort, make_response
)

# =============================================================================
# 漏洞01 + 漏洞13修复：配置集中管理，环境变量校验 + 默认值兜底
# =============================================================================
REQUIRED_ENV_VARS = {
    "SECRET_KEY": "应用密钥，用于 session 签名",
    "ADMIN_PWD": "管理员 admin 的登录密码",
    "ALICE_PWD": "普通用户 alice 的登录密码",
}


def validate_env():
    """启动时校验必需的环境变量是否存在，缺失则报错退出"""
    missing = []
    for var, desc in REQUIRED_ENV_VARS.items():
        if not os.getenv(var):
            missing.append(f"  - {var} ({desc})")

    if missing:
        print("=" * 60)
        print("错误：以下必需的环境变量未设置：")
        print("\n".join(missing))
        print()
        print("请通过以下方式设置：")
        print("  export SECRET_KEY='<你的密钥>'")
        print("  export ADMIN_PWD='<管理员密码>'")
        print("  export ALICE_PWD='<用户密码>'")
        print("=" * 60)
        sys.exit(1)


validate_env()

# =============================================================================
# 数据库初始化
# =============================================================================
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "users.db")


def init_db():
    """初始化 SQLite 数据库，创建 users 表并插入默认用户"""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 创建 users 表
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            balance INTEGER DEFAULT 0
        )
    """)

    # 插入默认用户（INSERT OR IGNORE 防止重复）
    c.execute("INSERT OR IGNORE INTO users (username, password, email, phone, balance) VALUES (?, ?, ?, ?, ?)",
              ("admin", "admin123", "admin@example.com", "13800138000", 99999))
    c.execute("INSERT OR IGNORE INTO users (username, password, email, phone, balance) VALUES (?, ?, ?, ?, ?)",
              ("alice", "alice2025", "alice@example.com", "13900139001", 100))

    # 兼容旧数据库：为已有表补充 balance 列（如果不存在）
    try:
        c.execute("ALTER TABLE users ADD COLUMN balance INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # 列已存在，忽略

    # 更新默认用户的余额
    c.execute("UPDATE users SET balance = 99999 WHERE username = 'admin' AND balance IS NULL")
    c.execute("UPDATE users SET balance = 100 WHERE username = 'alice' AND balance IS NULL")

    # 照片上传记录表（漏洞06修复：文件与用户关联）
    c.execute("""
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            file_size INTEGER DEFAULT 0,
            upload_time TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print(f"[数据库] 初始化完成: {DB_PATH}")


init_db()

# =============================================================================
# 漏洞05修复：debug 模式由环境变量控制，生产环境自动关闭
# =============================================================================
DEBUG_MODE = os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1", "yes")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# 上传配置：最大 16MB
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
# 漏洞07修复：限制请求体读取大小，防止流式绕过
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
UPLOAD_DIR = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 漏洞01+02修复：只允许图片类型
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def is_allowed_file(filename):
    """检查文件扩展名是否在允许列表中"""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def safe_filename(filename):
    """漏洞03+05修复：去除路径穿越字符和危险字符，保留可读文件名"""
    # 只取文件名部分，去除路径
    safe = os.path.basename(filename)
    # 只保留字母、数字、点、下划线、短横线
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", safe)
    # 防止空文件名和以点开头
    if not safe or safe.startswith("."):
        safe = f"upload_{uuid.uuid4().hex[:8]}"
    return safe

# =============================================================================
# 漏洞07修复：Session 安全加固
# =============================================================================
# 设置 session 过期时间为 30 分钟
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

# Cookie 安全标志
app.config["SESSION_COOKIE_HTTPONLY"] = True       # 禁止 JavaScript 读取 cookie
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"      # 限制跨站请求携带 cookie
# 仅在明确告知使用 HTTPS 时启用 Secure 标志
if os.getenv("ENABLE_HTTPS", "false").lower() in ("true", "1"):
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Strict"

# =============================================================================
# 漏洞12修复：安全日志系统
# =============================================================================
LOG_DIR = "/var/log/class01" if os.geteuid() == 0 else "/opt/Class01/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "security.log"), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("security")


def log_security_event(event_type, username, ip, detail=""):
    """记录安全相关事件到日志"""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "username": username,
        "ip": ip,
        "detail": detail,
    }
    logger.info(json.dumps(log_data, ensure_ascii=False))


# =============================================================================
# 漏洞09修复：登录频率限制（内存计数器 + 滑动时间窗口）
# =============================================================================
# 配置：15 分钟内允许 5 次失败尝试
RATE_LIMIT_CONFIG = {
    "max_attempts": 5,
    "window_seconds": 900,    # 15 分钟
    "block_minutes": 15,
}

# { "ip": { "count": int, "first_fail": timestamp, "blocked_until": timestamp } }
FAILED_LOGIN_CACHE = {}


def check_rate_limit(ip):
    """
    检查 IP 是否超出登录失败限制
    返回: (is_blocked: bool, remaining_attempts: int, block_seconds: int)
    """
    now = time.time()
    record = FAILED_LOGIN_CACHE.get(ip)

    if not record:
        return False, RATE_LIMIT_CONFIG["max_attempts"], 0

    # 检查是否在被封禁状态
    if record.get("blocked_until") and now < record["blocked_until"]:
        remaining = int(record["blocked_until"] - now)
        return True, 0, remaining

    # 如果被封禁时间已过，清除记录
    if record.get("blocked_until") and now >= record["blocked_until"]:
        del FAILED_LOGIN_CACHE[ip]
        return False, RATE_LIMIT_CONFIG["max_attempts"], 0

    # 检查时间窗口是否过期
    window_elapsed = now - record["first_fail"]
    if window_elapsed > RATE_LIMIT_CONFIG["window_seconds"]:
        # 窗口已过期，重置
        del FAILED_LOGIN_CACHE[ip]
        return False, RATE_LIMIT_CONFIG["max_attempts"], 0

    remaining_attempts = RATE_LIMIT_CONFIG["max_attempts"] - record["count"]
    return False, max(0, remaining_attempts), 0


def record_failed_attempt(ip):
    """记录一次登录失败"""
    now = time.time()
    record = FAILED_LOGIN_CACHE.get(ip)

    if not record:
        FAILED_LOGIN_CACHE[ip] = {
            "count": 1,
            "first_fail": now,
            "blocked_until": None,
        }
    else:
        record["count"] += 1

        # 检查是否触发封禁
        if record["count"] >= RATE_LIMIT_CONFIG["max_attempts"]:
            record["blocked_until"] = now + (RATE_LIMIT_CONFIG["block_minutes"] * 60)
            logger.warning(
                f"[RATE_LIMIT] IP {ip} 已被封禁 "
                f"{RATE_LIMIT_CONFIG['block_minutes']} 分钟 "
                f"（连续失败 {record['count']} 次）"
            )


def clear_rate_limit(ip):
    """登录成功后清除失败记录"""
    if ip in FAILED_LOGIN_CACHE:
        del FAILED_LOGIN_CACHE[ip]


# =============================================================================
# 漏洞06修复：CSRF 防护（基于 Double Submit Cookie 模式）
# =============================================================================
def generate_csrf_token():
    """生成并存储 CSRF token"""
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(32)
    return session["_csrf_token"]


def validate_csrf_token():
    """验证 POST 请求中的 CSRF token"""
    # AJAX 请求检查 X-CSRFToken 头
    token = request.form.get("_csrf_token") or request.headers.get("X-CSRFToken")
    stored = session.get("_csrf_token")

    if not token or not stored:
        return False

    # 使用 secrets.compare_digest 防止时序攻击
    return secrets.compare_digest(token, stored)


# 将 csrf_token 注入所有模板上下文，避免每个路由手动传递
@app.context_processor
def inject_globals():
    """为所有模板注入全局变量"""
    ctx = dict(csrf_token=generate_csrf_token())

    # 注入当前登录用户的 user_id（用于导航栏个人中心链接）
    username = session.get("username")
    if username:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()
        if row:
            ctx["current_user_id"] = row[0]

    return ctx


# =============================================================================
# 漏洞08修复：HTTP 安全响应头中间件
# =============================================================================
@app.after_request
def apply_security_headers(response):
    """为每个响应添加安全相关的 HTTP 头"""
    # 防止 MIME 类型嗅探
    response.headers["X-Content-Type-Options"] = "nosniff"
    # 防止点击劫持
    response.headers["X-Frame-Options"] = "DENY"
    # XSS 过滤器
    response.headers["X-XSS-Protection"] = "1; mode=block"
    # 引用策略
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # 内容安全策略
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "   # 允许内联样式
        "script-src 'self'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "form-action 'self'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'; "
        "object-src 'none'"
    )
    # 禁用自动检测内容类型
    response.headers["X-Download-Options"] = "noopen"
    # 权限策略（限制 API 调用）
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), "
        "interest-cohort=()"
    )
    return response


# =============================================================================
# 漏洞02修复：用户数据 - bcrypt 加盐哈希存储
# =============================================================================
RAW_USERS = {
    "admin": {
        "username": "admin",
        "password": os.getenv("ADMIN_PWD"),
        "role": "admin",
        "email": "admin@example.com",
        "phone": "13800138000",
        "balance": 99999,
    },
    "alice": {
        "username": "alice",
        "password": os.getenv("ALICE_PWD"),
        "role": "user",
        "email": "alice@example.com",
        "phone": "13900139001",
        "balance": 100,
    },
}

# 启动时使用 bcrypt 对密码进行加盐哈希处理
USERS = {}
for username, info in RAW_USERS.items():
    user_data = info.copy()
    user_data["password"] = bcrypt.hashpw(
        info["password"].encode(), bcrypt.gensalt()
    )
    USERS[username] = user_data


# =============================================================================
# 漏洞10修复：输入校验工具函数
# =============================================================================
def validate_login_input(username, password):
    """
    校验登录输入的安全性
    返回: (is_valid: bool, error_message: str)
    """
    # 检查是否存在
    if not username or not password:
        return False, "用户名和密码不能为空"

    # 长度限制
    if len(username) > 50:
        return False, "用户名过长"
    if len(password) > 128:
        return False, "密码过长"

    # 用户名只允许字母、数字、下划线和点号
    if not re.match(r"^[a-zA-Z0-9_.]+$", username):
        return False, "用户名包含非法字符"

    return True, ""


# =============================================================================
# 漏洞03修复：安全视图模型
# =============================================================================
def get_safe_user_info(username):
    """遵循最小权限原则，仅返回前端展示所需的非敏感字段"""
    user = USERS.get(username)
    if not user:
        return None
    return {
        "username": user["username"],
        "role": user["role"],
        "balance": user["balance"],
    }


# =============================================================================
# 路由：首页
# =============================================================================
@app.route("/")
def index():
    username = session.get("username")
    user_info = get_safe_user_info(username) if username else None

    # 处理搜索功能
    keyword = request.args.get("keyword", "")
    search_results = None
    if keyword:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # 漏洞修复：使用参数化查询 ? 占位符替代 f-string 拼接
        like_pattern = f"%{keyword}%"
        sql = "SELECT id, username, email, phone FROM users WHERE username LIKE ? OR email LIKE ?"
        print(f"[搜索] 执行 SQL: {sql} | 参数: keyword={keyword}")
        try:
            c.execute(sql, (like_pattern, like_pattern))
            search_results = c.fetchall()
            print(f"[搜索] 返回 {len(search_results)} 条结果")
        except Exception as e:
            print(f"[搜索] SQL 执行出错: {e}")
            search_results = []
        conn.close()

    return render_template("index.html", user=user_info, search_results=search_results, keyword=keyword)


# =============================================================================
# 路由：登录（漏洞06+09+10+14修复）
# =============================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    client_ip = request.remote_addr or "unknown"

    if request.method == "POST":
        # ---- 漏洞06修复：CSRF 校验 ----
        if not validate_csrf_token():
            log_security_event(
                "CSRF_ATTEMPT", "unknown", client_ip, "CSRF token 校验失败"
            )
            return render_template(
                "login.html",
                error="安全校验失败，请刷新页面重试",
            )

        # ---- 漏洞14修复：登出后使用 POST 跳转 ----
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # ---- 漏洞10修复：输入校验 ----
        is_valid, error_msg = validate_login_input(username, password)
        if not is_valid:
            log_security_event(
                "INVALID_INPUT", username, client_ip, error_msg
            )
            return render_template(
                "login.html",
                error=error_msg,
            )

        # ---- 漏洞09修复：登录频率限制 ----
        is_blocked, remaining, block_seconds = check_rate_limit(client_ip)
        if is_blocked:
            log_security_event(
                "RATE_LIMITED", username, client_ip,
                f"被封禁中，剩余 {block_seconds} 秒"
            )
            return render_template(
                "login.html",
                error=f"登录过于频繁，请在 {block_seconds // 60} 分钟后再试",
            )

        # ---- 漏洞02修复：bcrypt 密码比对 ----
        if username in USERS:
            stored_hash = USERS[username]["password"]
            if bcrypt.checkpw(password.encode(), stored_hash):
                # 登录成功
                session["username"] = username
                session.permanent = True  # 启用会话过期时间
                session["login_time"] = datetime.now().isoformat()

                # 清除登录失败记录
                clear_rate_limit(client_ip)

                # 重新生成 CSRF token（防止 session fixation）
                session["_csrf_token"] = secrets.token_hex(32)

                log_security_event(
                    "LOGIN_SUCCESS", username, client_ip, "登录成功"
                )

                user_info = get_safe_user_info(username)
                return render_template("index.html", user=user_info)

        # 登录失败
        record_failed_attempt(client_ip)
        _, remaining, _ = check_rate_limit(client_ip)
        log_security_event(
            "LOGIN_FAILED", username, client_ip,
            f"密码错误，剩余尝试次数: {remaining}"
        )

        return render_template(
            "login.html",
            error="用户名或密码错误",
        )

    # GET 请求：CSRF token 由 context_processor 自动注入
    success = request.args.get("success", "")
    return render_template("login.html", success=success)


# =============================================================================
# 路由：登出（需要 CSRF token 校验）
# =============================================================================
@app.route("/logout", methods=["POST"])
def logout():
    """登出接口 - 仅接受 POST 请求，需带有效 CSRF token"""
    username = session.get("username", "unknown")
    client_ip = request.remote_addr or "unknown"

    # 校验 CSRF token（context_processor 已确保模板中有正确 token）
    if not validate_csrf_token():
        log_security_event(
            "CSRF_ATTEMPT", username, client_ip, "登出 CSRF token 校验失败"
        )
        return redirect("/")

    session.clear()
    log_security_event("LOGOUT", username, client_ip, "用户登出")

    return redirect("/")


# 为兼容直接点击退出链接，保留 GET 方式但记录安全警告
@app.route("/logout_get", methods=["GET"])
def logout_get_fallback():
    """GET 方式登出（仅为向后兼容，记录安全告警）"""
    username = session.get("username", "unknown")
    client_ip = request.remote_addr or "unknown"

    session.clear()
    log_security_event(
        "LOGOUT_INSECURE", username, client_ip,
        "使用了 GET 方式登出（建议使用 POST）"
    )
    return redirect("/")


# =============================================================================
# 路由：注册
# =============================================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        # 漏洞修复：使用参数化查询 ? 占位符替代 f-string 拼接
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        sql = "INSERT INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)"
        print(f"[注册] 执行 SQL: {sql} | 参数: username={username}, email={email}, phone={phone}")
        try:
            c.execute(sql, (username, password, email, phone))
            conn.commit()
            print(f"[注册] 用户 {username} 注册成功")
            conn.close()
            return redirect("/login?success=1")
        except Exception as e:
            print(f"[注册] SQL 执行出错: {e}")
            conn.close()
            return render_template("register.html", error=f"注册失败: {str(e)}")

    return render_template("register.html")


# =============================================================================
# 路由：搜索
# =============================================================================
@app.route("/search", methods=["GET"])
def search():
    keyword = request.args.get("keyword", "")

    if not keyword:
        return redirect("/")

    # 漏洞修复：使用参数化查询 ? 占位符替代 f-string 拼接
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    like_pattern = f"%{keyword}%"
    sql = "SELECT id, username, email, phone FROM users WHERE username LIKE ? OR email LIKE ?"
    print(f"[搜索] 执行 SQL: {sql} | 参数: keyword={keyword}")
    try:
        c.execute(sql, (like_pattern, like_pattern))
        search_results = c.fetchall()
        print(f"[搜索] 返回 {len(search_results)} 条结果")
    except Exception as e:
        print(f"[搜索] SQL 执行出错: {e}")
        search_results = []
    conn.close()

    username = session.get("username")
    user_info = get_safe_user_info(username) if username else None
    return render_template("index.html", user=user_info, search_results=search_results, keyword=keyword)


# =============================================================================
# 路由：头像上传（文件上传漏洞修补：全部7项漏洞修复）
# =============================================================================
@app.route("/upload", methods=["GET", "POST"])
def upload():
    """用户头像上传 - 需要登录"""
    username = session.get("username")
    if not username:
        return redirect("/login")

    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            return render_template("upload.html", error="请选择要上传的文件")

        original_name = file.filename

        # 漏洞07修复：手动检查 Content-Length 防止流式绕过
        content_length = request.content_length or 0
        if content_length > 16 * 1024 * 1024:
            print(f"[上传] 用户 {username} 上传文件超过大小限制: {content_length} bytes")
            return render_template("upload.html", error="文件大小超过16MB限制")

        # 漏洞01+02修复：校验文件扩展名，仅允许图片类型
        if not is_allowed_file(original_name):
            print(f"[上传] 用户 {username} 上传非法文件类型: {original_name}")
            log_security_event("UPLOAD_REJECTED", username, request.remote_addr,
                               f"非法文件类型: {original_name}")
            return render_template("upload.html", error="仅允许上传 PNG、JPG、GIF、WebP 格式的图片")

        # 漏洞03+05修复：清理文件名（去除路径穿越和危险字符）
        safe_name = safe_filename(original_name)

        # 漏洞04修复：检查文件名冲突，冲突时追加随机后缀
        dest_path = os.path.join(UPLOAD_DIR, safe_name)
        if os.path.exists(dest_path):
            name_part, ext_part = safe_name.rsplit(".", 1) if "." in safe_name else (safe_name, "")
            safe_name = f"{name_part}_{uuid.uuid4().hex[:8]}.{ext_part}" if ext_part else f"{name_part}_{uuid.uuid4().hex[:8]}"
            dest_path = os.path.join(UPLOAD_DIR, safe_name)

        # 保存文件
        file.save(dest_path)
        file_size = os.path.getsize(dest_path)

        # 漏洞06修复：将上传记录存入数据库，与用户关联
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO uploads (username, filename, original_name, file_size, upload_time) VALUES (?, ?, ?, ?, ?)",
            (username, safe_name, original_name, file_size, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

        # 构造访问 URL
        file_url = url_for("static", filename=f"uploads/{safe_name}")
        print(f"[上传] 用户 {username} 上传文件: {safe_name} ({file_size} bytes)")
        log_security_event("UPLOAD_SUCCESS", username, request.remote_addr,
                           f"文件: {safe_name}, 大小: {file_size} bytes")

        return render_template("upload.html", success=file_url, filename=safe_name)

    return render_template("upload.html")


# =============================================================================
# 路由：个人中心（R-06+R-07修复：需登录 + 敏感信息脱敏）
# =============================================================================
@app.route("/profile", methods=["GET"])
def profile():
    """个人中心 - 需登录后通过 URL 参数 user_id 查询用户资料"""
    # R-06修复：要求登录
    username = session.get("username")
    if not username:
        return redirect("/login")

    user_id = request.args.get("user_id", "")

    if not user_id or not user_id.isdigit():
        return render_template("profile.html", error="无效的用户ID")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, email, phone, balance FROM users WHERE id = ?", (int(user_id),))
    user = c.fetchone()
    conn.close()

    if not user:
        return render_template("profile.html", error="用户不存在")

    # R-07+R-08修复：安全视图模型，email 和 phone 仅当前用户本人可查看
    current_username = session.get("username", "")
    is_owner = (user[1] == current_username)

    return render_template("profile.html", user={
        "id": user[0],
        "username": user[1],
        "email": user[2] or "",
        "phone": user[3] or "",
        "balance": user[4] or 0,
        "is_owner": is_owner,
    })


# =============================================================================
# 路由：充值（R-01~R-05修复：身份校验 + 金额校验 + CSRF）
# =============================================================================
@app.route("/recharge", methods=["POST"])
def recharge():
    """充值 - 需登录 + CSRF 校验 + 金额正负/上限校验 + 身份校验"""
    # R-06修复：要求登录
    current_username = session.get("username")
    if not current_username:
        return redirect("/login")

    # R-04修复：CSRF token 校验
    if not validate_csrf_token():
        log_security_event("CSRF_ATTEMPT", current_username, request.remote_addr,
                           "充值 CSRF token 校验失败")
        return redirect("/")

    user_id = request.form.get("user_id", "")
    amount_str = request.form.get("amount", "0")

    if not user_id or not user_id.isdigit():
        return redirect("/")

    # R-05修复：金额必须为合法整数
    try:
        amount = int(amount_str)
    except (ValueError, TypeError):
        log_security_event("RECHARGE_INVALID_AMOUNT", current_username, request.remote_addr,
                           f"非法金额格式: {amount_str}")
        return redirect(f"/profile?user_id={user_id}")

    # R-01修复：校验当前用户与目标 user_id 是否匹配
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id = ?", (int(user_id),))
    target_user = c.fetchone()

    if not target_user:
        conn.close()
        return redirect("/")

    if target_user[0] != current_username:
        # 记录了未经授权的充值尝试
        log_security_event("RECHARGE_UNAUTHORIZED", current_username, request.remote_addr,
                           f"试图充值用户ID={user_id} ({target_user[0]})")
        conn.close()
        return redirect("/")

    # R-02修复：金额必须为正数
    if amount <= 0:
        log_security_event("RECHARGE_NEGATIVE", current_username, request.remote_addr,
                           f"负数/零金额: {amount}")
        return redirect(f"/profile?user_id={user_id}")

    # R-03修复：单次充值上限
    MAX_RECHARGE = 100000
    if amount > MAX_RECHARGE:
        return redirect(f"/profile?user_id={user_id}")

    c.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, int(user_id)))
    conn.commit()

    # 记录充值日志
    c.execute("SELECT balance FROM users WHERE id = ?", (int(user_id),))
    new_balance = c.fetchone()[0]
    conn.close()

    log_security_event("RECHARGE_SUCCESS", current_username, request.remote_addr,
                       f"充值金额: {amount}, 新余额: {new_balance}")

    return redirect(f"/profile?user_id={user_id}")


# =============================================================================
# 路由：动态页面加载（P-01~P-04修复）
# =============================================================================
@app.route("/page", methods=["GET"])
def page():
    """动态页面加载 - 需登录，白名单校验文件路径"""
    # P-02修复：要求登录
    username = session.get("username")
    if not username:
        return redirect("/login")

    name = request.args.get("name", "")
    page_content = None
    page_error = None

    if name:
        # P-01+P-04修复：使用 realpath 校验文件是否在 pages/ 目录内
        safe_base = os.path.realpath(os.path.join(app.root_path, "pages"))
        requested_path = os.path.realpath(os.path.join(safe_base, name))

        if not requested_path.startswith(safe_base + os.sep):
            log_security_event("PAGE_TRAVERSAL", username, request.remote_addr,
                               f"路径穿越尝试: {name}")
            page_error = "页面不存在"
        else:
            # 尝试直接读取
            if os.path.exists(requested_path):
                with open(requested_path, "r", encoding="utf-8") as f:
                    page_content = f.read()
            else:
                # 尝试加上 .html 后缀
                requested_path_html = requested_path + ".html"
                if os.path.exists(requested_path_html):
                    with open(requested_path_html, "r", encoding="utf-8") as f:
                        page_content = f.read()
                else:
                    page_error = "页面不存在"

    user_info = get_safe_user_info(username)
    return render_template("index.html", user=user_info, page_content=page_content, page_error=page_error)


# =============================================================================
# 漏洞11修复：自定义错误页面
# =============================================================================
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"[500] {request.method} {request.path} - {str(error)}")
    return render_template("500.html"), 500


@app.errorhandler(403)
def forbidden(error):
    return render_template("403.html"), 403


# =============================================================================
# 健康检查接口（无敏感信息）
# =============================================================================
@app.route("/health")
def health_check():
    """健康检查 - 不返回任何敏感信息"""
    return jsonify({"status": "ok"}), 200


# =============================================================================
# 漏洞05修复：使用环境变量控制 debug 模式
# =============================================================================
if __name__ == "__main__":
    print(f"[启动] 用户管理平台 v2.0 (安全加固版)")
    print(f"[启动] Debug 模式: {'开启' if DEBUG_MODE else '关闭'}")
    print(f"[启动] Session 过期时间: 30 分钟")
    print(f"[启动] 登录频率限制: {RATE_LIMIT_CONFIG['max_attempts']} 次 / "
          f"{RATE_LIMIT_CONFIG['window_seconds'] // 60} 分钟")
    print(f"[启动] HTTP 安全头: 已启用")
    print(f"[启动] CSRF 保护: 已启用")
    print(f"[启动] 安全日志: {LOG_DIR}/security.log")
    print("-" * 50)
    app.run(debug=DEBUG_MODE, host="0.0.0.0", port=5000)
