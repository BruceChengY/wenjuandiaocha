"""
配置文件
定义应用的各种配置参数
"""

import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置类"""
    
    # API配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # CORS配置
    allowed_origins: List[str] = [
        "chrome-extension://*",
        "http://localhost:*",
        "https://localhost:*",
        "http://127.0.0.1:*",
        "https://127.0.0.1:*"
    ]
    
    # Redis配置（可选）
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    redis_enabled: bool = False
    
    # 缓存配置
    cache_ttl: int = 86400  # 24小时（秒）
    max_cache_size: int = 10000  # 最大缓存条目数
    
    # 翻译配置
    max_text_length: int = 5000
    default_source_lang: str = "en"
    default_target_lang: str = "zh-cn"
    translator_type: str = "google"  # google, baidu, youdao
    
    # 百度翻译配置（如果使用）
    baidu_app_id: str = ""
    baidu_secret_key: str = ""
    
    # 有道翻译配置（如果使用）
    youdao_app_key: str = ""
    youdao_app_secret: str = ""
    
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "translator.log"
    
    # 性能配置
    max_concurrent_requests: int = 100
    request_timeout: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 创建全局配置实例
settings = Settings()

# 根据环境变量更新配置
if os.getenv("ENVIRONMENT") == "production":
    settings.debug = False
    settings.log_level = "WARNING"
    settings.api_host = "0.0.0.0"
    
if os.getenv("REDIS_URL"):
    settings.redis_enabled = True
    # 解析Redis URL（如果提供）
    redis_url = os.getenv("REDIS_URL")
    if redis_url.startswith("redis://"):
        # 简单的Redis URL解析
        parts = redis_url.replace("redis://", "").split(":")
        if len(parts) >= 2:
            settings.redis_host = parts[0]
            try:
                settings.redis_port = int(parts[1].split("/")[0])
            except ValueError:
                pass