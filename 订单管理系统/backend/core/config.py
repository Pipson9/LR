from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置。

    真实值放在项目根目录的 ``.env`` 里（已被 .gitignore 排除，不会进仓库）；
    这里写的只是占位默认值，克隆者需要复制 .env.example 为 .env 后填入自己的配置。
    """

    # 注意驱动必须是 asyncmy（异步驱动）而不是 pymysql（同步驱动）——
    # 因为 database.py 里用的是 create_async_engine，同步驱动配异步引擎会直接报 NoSuchModuleError
    database_url: str = Field(
        default="mysql+asyncmy://user:password@127.0.0.1:3306/fastapi_demo",
        alias="DATABASE_URL",
    )
    secret_key: str = Field(
        default="change-me-to-a-random-string",
        alias="SECRET_KEY",
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        # 允许通过 DATABASE_URL / SECRET_KEY 这类大写环境变量名覆盖
        "populate_by_name": True,
        "extra": "ignore",
    }


settings = Settings()
