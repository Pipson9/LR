"""
图形验证码模块（零状态、内存存储）

设计要点：
- 验证码放在进程内存的字典里，带 5 分钟过期时间，不依赖 Redis/数据库
- captcha_id 由前端拿着去登录，确保“先拿图、再登录”是同一次会话
- 验证码校验是一次性的：校验过就删除，防止重放
- 仅用于演示/学习，生产环境建议换成 Redis + 限流
"""
import base64
import io
import random
import string
import time
import uuid

from PIL import Image, ImageDraw, ImageFont

# captcha_id -> {"code": str, "expire": float}
_CAPTCHA_STORE: dict = {}
_CAPTCHA_TTL = 300  # 秒，5 分钟


def _gen_code(length: int = 4) -> str:
    """生成验证码字符：去掉易混淆的 0/O/1/I/L 等"""
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(random.choices(chars, k=length))


def _gen_id() -> str:
    return uuid.uuid4().hex


def _draw_image(code: str) -> bytes:
    """用 Pillow 画一张带干扰线的验证码图片，返回 PNG 字节"""
    width, height = 120, 40
    img = Image.new("RGB", (width, height), (240, 245, 250))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except Exception:
        font = ImageFont.load_default()

    # 干扰线
    for _ in range(4):
        draw.line(
            [
                (random.randint(0, width), random.randint(0, height)),
                (random.randint(0, width), random.randint(0, height)),
            ],
            fill=(
                random.randint(120, 200),
                random.randint(120, 200),
                random.randint(120, 200),
            ),
            width=1,
        )

    # 字符
    for i, ch in enumerate(code):
        color = (
            random.randint(0, 120),
            random.randint(0, 120),
            random.randint(0, 120),
        )
        draw.text((10 + i * 26, 5), ch, font=font, fill=color)

    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def create_captcha():
    """生成验证码，返回 (captcha_id, base64_png, code)"""
    captcha_id = _gen_id()
    code = _gen_code()
    _CAPTCHA_STORE[captcha_id] = {"code": code, "expire": time.time() + _CAPTCHA_TTL}
    png = _draw_image(code)
    b64 = base64.b64encode(png).decode("ascii")
    return captcha_id, f"data:image/png;base64,{b64}", code


def verify_captcha(captcha_id: str | None, code: str | None) -> bool:
    """校验验证码；无论成功失败都删除该 id（一次性），过期也返回 False"""
    if not captcha_id or not code:
        return False
    item = _CAPTCHA_STORE.pop(captcha_id, None)
    if not item:
        return False
    if time.time() > item["expire"]:
        return False
    return item["code"].upper() == code.strip().upper()


def cleanup_expired():
    """顺手清理过期验证码，避免内存无限增长"""
    now = time.time()
    expired = [k for k, v in _CAPTCHA_STORE.items() if now > v["expire"]]
    for k in expired:
        _CAPTCHA_STORE.pop(k, None)
