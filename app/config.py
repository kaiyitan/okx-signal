from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    okx_ws_url: str = "wss://ws.okx.com:8443/ws/v5/public"
    okx_rest_url: str = "https://www.okx.com"
    coingecko_api_url: str = "https://api.coingecko.com/api/v3"
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str | None = None
    redis_ssl: bool = False
    cache_raw_response: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
