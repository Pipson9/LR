# -*- coding: utf-8 -*-
"""端到端验证脚本：注册 -> 验证码 -> 登录 -> 带令牌访问业务接口（用 TestClient 在同进程内读取验证码）"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import pathlib
ROOT = str(pathlib.Path(__file__).resolve().parent.parent)  # backend/ 目录
sys.path.insert(0, ROOT)  # 加入搜索路径（相对路径，不依赖本机绝对路径）

from fastapi.testclient import TestClient
import captcha as cap
import main

c = TestClient(main.app)
user = "e2e_tester"

# 1. 注册（已存在则忽略报错）
r = c.post("/users/", json={"username": user, "email": "e2e@test.com", "password": "123456"})
print("注册:", r.status_code, r.json().get("username") or r.json().get("detail"))

# 2. 拿验证码（同进程，从内存读出正确 code）
r = c.get("/captcha")
cid = r.json()["captcha_id"]
code = cap._CAPTCHA_STORE[cid]["code"]
print("验证码: id=%s... code=%s (同进程读取)" % (cid[:8], code))

# 3. 正确验证码 + 正确密码登录
r = c.post("/login", data={"username": user, "password": "123456", "code": code, "captcha_id": cid})
print("登录:", r.status_code)
assert r.status_code == 200, r.text
token = r.json()["access_token"]
H = {"Authorization": f"Bearer {token}"}

# 4. 验证码一次性：同一 id 再用应失败
r2 = c.post("/login", data={"username": user, "password": "123456", "code": code, "captcha_id": cid})
print("验证码重放:", r2.status_code, r2.json()["detail"])

# 5. 错误密码 + 新验证码
r = c.get("/captcha"); cid = r.json()["captcha_id"]
code = cap._CAPTCHA_STORE[cid]["code"]
r = c.post("/login", data={"username": user, "password": "wrong", "code": code, "captcha_id": cid})
print("错误密码:", r.status_code, r.json()["detail"])

# 6. 带令牌访问业务接口
print("GET /products/:", c.get("/products/", headers=H, params={"page": 1, "page_size": 5}).status_code)
print("GET /orders/:", c.get("/orders/", headers=H).status_code)

# 7. 从 JWT 解析 user_id 再查个人信息（前端就是这么做的）
import base64, json as j
payload = token.split(".")[1]
payload += "=" * (-len(payload) % 4)
uid = j.loads(base64.urlsafe_b64decode(payload))["user_id"]
r = c.get(f"/users/{uid}", headers=H)
print("GET /users/{id}:", r.status_code, r.json()["username"])

# 8. 未带令牌访问应 401
print("无令牌访问 /products/:", c.get("/products/").status_code)

print("\n=== 端到端测试全部通过 ===")
