from jose import jwt, JWTError   # JWTError 是 jose 里所有令牌异常的基类，接住它就够用
from datetime import datetime, timedelta

# 密钥不再写死在代码里，改为统一从 core/config.py 读取（真实值来自 .env，不进仓库）
from core.config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm          # 表示 JWT 使用什么算法生成签名。
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes  # 默认 1440（24 小时）
def create_token(data: dict):   #创建令牌（token）
    to_encode = data.copy()  #把用户传进的data拷贝一份，避免修改原数据
    #to_encode,实际上就是用户穿进来的user_id
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})   #在字典to_encode新增exp属性
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    #jwt.encode把to_encode,SECRET_KEY,ALGORITHM编码，得到一个字符串令牌

def decode_token(token: str) :
    # 令牌被篡改/伪造/过期时，jwt.decode 会直接"抛异常"而不是返回 None，
    # 所以必须用 try 把异常接住并返回 None，否则用户会收到 500（服务器错误）而不是 401（未认证）
    # 这也是新手最常踩的坑之一：伪造令牌一测就 500
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    except JWTError:   # 签名不对、格式不对、过期，都属于这类异常
        return None
    user_id = payload.get("user_id")
    if user_id is None:
        return None
    return int(user_id)