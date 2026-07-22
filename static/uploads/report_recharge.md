# 充值功能与个人中心漏洞修复报告

| 项目 | 内容 |
|------|------|
| 项目路径 | /opt/Class01 |
| 审计日期 | 2026-07-22 |
| 修复状态 | ✅ **8/8 全部完成** |
| 风险等级 | 修复前：🔴 严重 → 修复后：🟢 安全 |

---

## 1. 漏洞概述

对 `/recharge` 和 `/profile` 路由进行安全审计，共发现 **8 个安全漏洞**，覆盖身份校验缺失、CSRF 保护缺失、金额输入校验缺失、信息泄露等多个攻击面。

### 1.1 漏洞清单

| 编号 | 漏洞名称 | 类型 | 严重程度 | 代码位置 |
|:----:|---------|------|:--------:|---------|
| R-01 | 无身份校验 | 任意余额操作 | 🔴 严重 | `recharge():736-744` |
| R-02 | 金额无正负校验 | 负数扣款 | 🔴 严重 | `recharge():737` |
| R-03 | 金额无上限限制 | 整数溢出/超额 | 🔴 严重 | `recharge():744` |
| R-04 | CSRF 校验缺失 | 跨站请求伪造 | 🟠 高危 | `recharge():733-748` |
| R-05 | 金额类型校验缺失 | 浮点数/字符串注入 | 🟡 中危 | `recharge():737` |
| R-06 | 个人中心未限制登录 | 信息泄露 | 🟠 高危 | `profile():704-727` |
| R-07 | 个人中心泄露敏感字段 | 信息泄露 | 🟠 高危 | `profile():721-727` |
| R-08 | 未使用安全视图模型 | 设计不一致 | 🟡 中危 | `profile()` vs `get_safe_user_info()` |

### 1.2 原始漏洞代码

```python
# 个人中心（修复前）
@app.route("/profile", methods=["GET"])
def profile():
    user_id = request.args.get("user_id", "")      # ❌ 无登录校验
    ...
    return render_template("profile.html", user={
        "email": ..., "phone": ..., "balance": ...  # ❌ 全部字段公开
    })

# 充值（修复前）
@app.route("/recharge", methods=["POST"])
def recharge():
    user_id = request.form.get("user_id", "")      # ❌ 无身份校验
    amount = request.form.get("amount", "0")        # ❌ 无格式/正负校验
    ...
    c.execute("UPDATE users SET balance = balance + ? WHERE id = ?",
              (amount, int(user_id)))               # ❌ 无CSRF校验、无上限
```

---

## 2. 漏洞详情与修复

### 2.1 R-01：无身份校验（🔴 严重）

**问题：** 充值路由不验证操作者身份，任意登录用户可修改任意用户的余额。

**实际验证：** alice 登录后 POST `user_id=1&amount=99999` → admin 余额增加。

**修复方案：** 从数据库查询目标用户，比对用户名与当前 session 用户名。

```python
# 修复后
c.execute("SELECT username FROM users WHERE id = ?", (int(user_id),))
target_user = c.fetchone()
if target_user[0] != current_username:
    log_security_event("RECHARGE_UNAUTHORIZED", ...)
    return redirect("/")
```

---

### 2.2 R-02：金额无正负校验（🔴 严重）

**问题：** `amount` 直接参与 `balance + amount` 计算，传入负数可盗取余额。

**实际验证：** 充 `-999999` → 余额从 100 变为 `-999899`。

**修复方案：** 充值前检查 `amount > 0`。

```python
if amount <= 0:
    return redirect(f"/profile?user_id={user_id}")
```

---

### 2.3 R-03：金额无上限限制（🔴 严重）

**问题：** 无最大值限制，充入 `999999999` 可导致余额膨胀。

**修复方案：** 设置单次充值上限。

```python
MAX_RECHARGE = 100000
if amount > MAX_RECHARGE:
    return redirect(f"/profile?user_id={user_id}")
```

---

### 2.4 R-04：CSRF 校验缺失（🟠 高危）

**问题：** `/recharge` 路由未调用 `validate_csrf_token()`，攻击者可在第三方网站构造表单跨站提交。

**实际验证：** 不带 `_csrf_token` 参数直接 POST → 充值成功。

**攻击场景：**
```html
<!-- 攻击者页面中的隐藏表单 -->
<form action="http://target/recharge" method="POST">
  <input type="hidden" name="user_id" value="2">
  <input type="hidden" name="amount" value="-50000">
  <input type="submit" id="submitBtn">
</form>
```

**修复方案：** 添加 CSRF token 校验。

```python
if not validate_csrf_token():
    log_security_event("CSRF_ATTEMPT", ...)
    return redirect("/")
```

---

### 2.5 R-05：金额类型校验缺失（🟡 中危）

**问题：** amount 未校验是否为合法整数，传入浮点数 `3.14` 导致余额变为浮点数。

**修复方案：** 使用 `int()` 转换并捕获异常。

```python
try:
    amount = int(amount_str)
except (ValueError, TypeError):
    return redirect(f"/profile?user_id={user_id}")
```

---

### 2.6 R-06：个人中心未限制登录（🟠 高危）

**问题：** `/profile` 路由未检查登录状态，未登录用户可直接访问任意用户资料。

**实际验证：** 无 Cookie 直接访问 `/profile?user_id=1` → 返回 admin 完整资料。

**修复方案：** 路由入口添加登录校验。

```python
username = session.get("username")
if not username:
    return redirect("/login")
```

---

### 2.7 R-07 + R-08：敏感信息泄露与安全视图（🟠 高危 + 🟡 中危）

**问题：** 个人中心无条件展示 email、phone 等敏感字段，其他用户可查看任意用户的隐私信息。与首页使用的 `get_safe_user_info()` 安全视图模型不一致。

**修复方案：** 引入 `is_owner` 标识，仅本人可查看完整信息，其他人看到脱敏提示。

```python
# 后端
is_owner = (user[1] == current_username)
return render_template("profile.html", user={..., "is_owner": is_owner})
```

```html
<!-- 前端模板 -->
{% if user.is_owner %}
  <li>邮箱：{{ user.email }}</li>
  <li>手机：{{ user.phone }}</li>
{% else %}
  <li>邮箱：<span class="info-masked">仅本人可见</span></li>
  <li>手机：<span class="info-masked">仅本人可见</span></li>
{% endif %}
```

---

## 3. 修复后验证测试

### 3.1 安全性测试

| 编号 | 测试用例 | 操作 | 修复前 | 修复后 | 状态 |
|:----:|---------|------|:------:|:------:|:----:|
| S-01 | 跨用户充值 | alice 给 admin 充 100 | 🔴 成功 | ✅ 被拦截（redirect /） | ✅ |
| S-02 | 负数充值 | 充 -500 | 🔴 余额减少 | ✅ 被拦截 | ✅ |
| S-03 | 超上限充值 | 充 999999（上限 100000） | 🔴 成功 | ✅ 被拦截 | ✅ |
| S-04 | 无 CSRF 充值 | 不带 `_csrf_token` POST | 🔴 成功 | ✅ 被拦截 | ✅ |
| S-05 | 字符串金额 | 充 "abc" | 🔴 异常 | ✅ 被拦截 | ✅ |
| S-06 | 浮点金额 | 充 3.14 | 🔴 余额变浮点 | ✅ 被拦截 | ✅ |
| S-07 | 未登录看个人中心 | 无 Cookie 访问 `/profile` | 🔴 可访问 | ✅ 302 跳转 `/login` | ✅ |
| S-08 | 非本人查看脱敏 | alice 看 admin 资料 | 🔴 全部可见 | ✅ 邮箱手机显示"仅本人可见" | ✅ |
| S-09 | 本人查看完整信息 | admin 看自己资料 | ✅ 可见 | ✅ 仍可见 | ✅ |
| S-10 | 正常充值 | admin 充 1000 | ✅ 成功 | ✅ 成功（99999→100999） | ✅ |

### 3.2 功能回归测试

| 编号 | 测试用例 | 操作 | 预期 | 结果 |
|:----:|---------|------|------|:----:|
| F-01 | 首页访问 | 无 cookie | 请先登录 | ✅ |
| F-02 | admin 登录 | admin/admin123 | 欢迎回来 | ✅ |
| F-03 | 用户搜索 | keyword=admin | 返回 admin@example.com | ✅ |
| F-04 | 注册页 | GET /register | HTTP 200 | ✅ |
| F-05 | 导航栏个人中心 | 已登录首页 | "个人中心"按钮可见 | ✅ |

**安全性测试：10/10 ✅ | 功能测试：5/5 ✅ | 综合通过率：15/15（100%）**

---

## 4. 修复对比与总结

### 4.1 攻击面对比

| 攻击类型 | 修复前 | 修复后 | 防御机制 |
|---------|:------:|:------:|---------|
| 跨用户恶意充值 | 🔴 可任意操作 | 🟢 身份校验拦截 | session 比对 |
| 负数扣款盗取余额 | 🔴 直接扣减 | 🟢 正数校验 | `amount > 0` |
| 超量充值制造混乱 | 🔴 无限制 | 🟢 上限 100,000 | `MAX_RECHARGE` |
| CSRF 跨站伪造充值 | 🔴 无校验 | 🟢 CSRF token 拦截 | `validate_csrf_token()` |
| 浮点数/字符串注入 | 🔴 余额变浮点 | 🟢 类型校验拦截 | `int()` + try/except |
| 未登录遍历用户资料 | 🔴 全部公开 | 🟢 需登录 | session 校验 |
| 非本人查看秘密信息 | 🔴 email/phone 泄露 | 🟢 脱敏显示 | `is_owner` 标识 |

### 4.2 修复后的处理流程

```
/profile:
  请求 → 登录校验 → 参数校验 → 查询用户
     → 本人? → 是: 显示完整信息 + 充值表单
            → 否: 脱敏显示（邮箱/手机隐藏）+ 无充值表单

/recharge:
  请求 → 登录校验 → CSRF 校验 → 身份校验 → 金额格式校验
     → 正数校验 → 上限校验 → 执行充值 → 日志记录 → 跳转
```

### 4.3 文件变更清单

| 文件 | 操作 | 涉及漏洞 |
|------|:----:|:--------:|
| `app.py` | ✅ 修改 | 全部 8 项 |
| `templates/profile.html` | ✅ 重写 | R-07, R-08 |
| `static/css/style.css` | ✅ 修改 | R-07（脱敏样式） |

**变更统计：** `profile()` 路由增加 10 行（登录校验 + is_owner），`recharge()` 路由增加 30 行（身份/CSRF/金额/日志校验），`profile.html` 增加条件脱敏逻辑。

---

*报告生成于 2026-07-22 | 安全巡检实施人: Claude Code*
