from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field


class Settings(BaseSettings):
    # Database Configuration (PostgreSQL)
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int
    database_url: Optional[str] = None
    
    # Web3 Configuration
    monad_rpc_url: Optional[str] = None
    monad_chain_id: int = Field(default=10143, alias="MONAD_TESTNET_CHAIN_ID")
    private_key: Optional[str] = None
    
    # JWT Configuration (POC에서는 사용하지 않음)
    """
    secret_key: Optional[str] = None
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    """
    
    # API Configuration
    api_v1_str: str
    project_name: str
    
    # Server Configuration
    server_host: str
    server_port: int
    
    # File Storage
    upload_dir: str
    max_file_size: int
    
    # Telegram Bot (Optional)
    telegram_bot_token: Optional[str] = None
    
    # Application Configuration
    debug: bool
    log_level: str
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # DATABASE_URL이 설정되지 않은 경우 자동 생성
        if not self.database_url:
            self.database_url = f"postgresql://{self.postgres_user}:{self.postgres_password}@localhost:{self.postgres_port}/{self.postgres_db}"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",  # 추가 필드 무시
        "env_prefix": "",   # 환경 변수 접두사 없음
    }


settings = Settings() 