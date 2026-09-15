# -*- coding: utf-8 -*-
"""演示数据生成脚本：用户 / 商品 / 优惠券 / 订单
可重复执行（按唯一键跳过已存在的数据）。
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import pathlib
import os
ROOT = str(pathlib.Path(__file__).resolve().parent.parent)  # backend/ 目录
sys.path.insert(0, ROOT)  # 加入搜索路径（相对路径，不依赖本机绝对路径）

import pymysql
from auth.security import hash_password

# 数据库连接信息优先读环境变量，取不到才用默认值。也可以在命令行传入：
#   DB_USER=root DB_PASSWORD=xxx DB_NAME=fastapi_demo python tests/seed_demo_data.py
CONN = dict(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "password"),
    database=os.getenv("DB_NAME", "fastapi_demo"),
    charset="utf8mb4",
)

# ---------- 1. 演示用户（密码统一 123456） ----------
DEMO_USERS = [
    ("zhangsan", "zhangsan@example.com", 0),
    ("lisi",     "lisi@example.com",     0),
    ("wangwu",   "wangwu@example.com",   0),
    ("zhaoliu",  "zhaoliu@example.com",  0),
]

# ---------- 2. 演示商品 ----------
DEMO_PRODUCTS = [
    ("无线蓝牙耳机 Pro",       299.0,  120, 1),
    ("机械键盘 87 键",         399.0,   80, 1),
    ("4K 显示器 27 英寸",     1599.0,   30, 1),
    ("USB-C 扩展坞",           199.0,  200, 1),
    ("人体工学椅",             899.0,   25, 1),
    ("智能手环 6 代",          249.0,  150, 1),
    ("便携移动电源 20000mAh",  129.0,  300, 1),
    ("降噪头戴耳机",           999.0,   45, 1),
    ("电竞鼠标",               159.0,  180, 1),
    ("旧款键盘（已下架）",      99.0,    0,  0),
]

# ---------- 3. 演示优惠券 ----------
import datetime as dt
DEMO_COUPONS = [
    ("新人专享券",   "NEW2026",     10.0,  100.0,  1000, 126,
     dt.datetime(2026, 8, 1),  dt.datetime(2026, 12, 31), "active"),
    ("满减券",       "FULL300",     30.0,  300.0,   500,  88,
     dt.datetime(2026, 8, 1),  dt.datetime(2026, 10, 31), "active"),
    ("老客回馈券",   "VIP888",      50.0,  500.0,   200,  45,
     dt.datetime(2026, 8, 15), dt.datetime(2026, 9, 30),  "active"),
    ("大促预热券",   "SALE618",     20.0,  200.0,  2000,  0,
     dt.datetime(2026, 9, 1),  dt.datetime(2026, 9, 18),  "inactive"),
    ("七夕限定券",   "QIXI520",     52.0,  520.0,   300, 300,
     dt.datetime(2026, 8, 1),  dt.datetime(2026, 8, 25),  "expired"),
]

# ---------- 4. 演示订单（覆盖 5 种状态） ----------
# (order_no, user_id, amount, status)
DEMO_ORDERS = [
    ("GP1001", 5,  1599.0, "paid"),
    ("GP1002", 6,   299.0, "paid"),
    ("GP1003", 6,   598.0, "shipped"),
    ("GP1004", 5,  1299.0, "shipped"),
    ("GP1005", 6,   399.0, "completed"),
    ("GP1006", 5,  1048.0, "completed"),
    ("GP1007", 6,   199.0, "pending"),
    ("GP1008", 5,   899.0, "pending"),
    ("GP1009", 6,   159.0, "cancelled"),
    ("GP1010", 5,   249.0, "cancelled"),
]


def main():
    conn = pymysql.connect(**CONN)
    cur = conn.cursor()
    added = {"users": 0, "products": 0, "coupons": 0, "orders": 0}

    # 1) 用户
    for username, email, is_admin in DEMO_USERS:
        cur.execute("SELECT id FROM users WHERE username=%s OR email=%s", (username, email))
        if cur.fetchone():
            print(f"[跳过] 用户 {username} 已存在")
            continue
        cur.execute(
            "INSERT INTO users (username, email, hashed_password, is_active, is_admin) "
            "VALUES (%s, %s, %s, 1, %s)",
            (username, email, hash_password("123456"), is_admin),
        )
        added["users"] += 1
    print(f"新增用户 {added['users']} 个（密码均为 123456）")

    # 2) 商品
    for name, price, stock, active in DEMO_PRODUCTS:
        cur.execute("SELECT id FROM products WHERE name=%s", (name,))
        if cur.fetchone():
            print(f"[跳过] 商品 {name} 已存在")
            continue
        cur.execute(
            "INSERT INTO products (name, price, stock, is_active) VALUES (%s, %s, %s, %s)",
            (name, price, stock, active),
        )
        added["products"] += 1
    print(f"新增商品 {added['products']} 个")

    # 3) 优惠券
    for row in DEMO_COUPONS:
        code = row[1]
        cur.execute("SELECT id FROM coupons WHERE code=%s", (code,))
        if cur.fetchone():
            print(f"[跳过] 优惠券 {code} 已存在")
            continue
        cur.execute(
            "INSERT INTO coupons (name, code, discount_amount, min_amount, total_count, "
            "used_count, start_time, end_time, status, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())",
            row,
        )
        added["coupons"] += 1
    print(f"新增优惠券 {added['coupons']} 张")

    # 4) 订单
    for order_no, user_id, amount, status in DEMO_ORDERS:
        cur.execute("SELECT order_id FROM orders WHERE order_no=%s", (order_no,))
        if cur.fetchone():
            print(f"[跳过] 订单 {order_no} 已存在")
            continue
        cur.execute(
            "INSERT INTO orders (order_no, user_id, amount, status) VALUES (%s, %s, %s, %s)",
            (order_no, user_id, amount, status),
        )
        added["orders"] += 1
    print(f"新增订单 {added['orders']} 条")

    conn.commit()
    print("\n==== 汇总 ====")
    for t in ["users", "products", "orders", "coupons"]:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"{t}: 共 {cur.fetchone()[0]} 条")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
