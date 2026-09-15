import bcrypt

# 【为什么不用 passlib？】
# 课程原代码用的是 passlib：
#     from passlib.context import CryptContext
#     pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# 但 passlib 从 2020 年起停止维护，和 pip 新装的 bcrypt 5.x 完全不兼容：
# 它读不到新版 bcrypt 的版本号（bcrypt 4.0 起移除了 __about__ 属性），
# 最终导致任何密码（哪怕只有 8 个字节）在哈希时都会抛
# "ValueError: password cannot be longer than 72 bytes"。
# 所以这里直接改用 bcrypt 官方库：函数名和用法保持不变，
# Router 里的调用代码一行都不用改，数据库里的旧哈希也完全兼容（格式都是 $2b$12$...）。

# bcrypt 算法有个硬性上限：只处理密码的前 72 字节。
# （英文/数字 1 字节；中文在 UTF-8 里 1 个字占 3 字节，约 24 个汉字就到顶）
# bcrypt 5.x 遇到超过 72 字节的密码会直接报错而不是悄悄截断，
# 所以这里统一显式截断，保证"注册时怎么哈希、登录时就怎么校验"，行为始终一致。
MAX_PASSWORD_BYTES = 72


def hash_password(password: str) -> str:
    """把明文密码变成哈希串（存进数据库的就是它）"""
    return bcrypt.hashpw(
        password.encode("utf-8")[:MAX_PASSWORD_BYTES],  # str -> bytes，并截断到算法上限
        bcrypt.gensalt(),                               # 自动生成随机盐（默认 12 轮强度）
    ).decode("ascii")                                   # 得到 "$2b$12$...." 形式的 60 字符哈希串


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    校验登录密码是否正确。
    注意：bcrypt 是"单向"哈希，没办法把数据库里的哈希还原成明文，
    所以只能拿"用户输入的明文"再算一次哈希，和数据库里存的比对是否一致。
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:MAX_PASSWORD_BYTES],
            hashed_password.encode("ascii"),
        )
    except (ValueError, AttributeError):
        # 数据库里存了格式不对的哈希（空串/脏数据/NULL）时 checkpw 会抛异常，
        # 按约定俗成的做法：当成"密码不正确"返回 False，而不是让接口报 500
        return False
