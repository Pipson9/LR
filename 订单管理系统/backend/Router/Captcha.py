"""验证码接口：GET /captcha 返回图片(base64) 与 captcha_id"""
from fastapi import APIRouter

from captcha import create_captcha

router = APIRouter(tags=["验证码"])


@router.get("/captcha")
async def get_captcha():
    """
    返回一个图形验证码：
    {
      "captcha_id": "xxx",                # 登录时要带回来
      "image": "data:image/png;base64,..." # 直接塞进 <img src>
    }
    """
    captcha_id, image, _code = create_captcha()
    return {"captcha_id": captcha_id, "image": image}
