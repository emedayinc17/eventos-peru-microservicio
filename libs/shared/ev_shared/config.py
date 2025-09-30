from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, computed_field, conint
from pathlib import Path

def vault_or_env_path():
    """
    Prioridad:
    1) /vault/secrets/config (si usas Vault Agent)
    2) .env del servicio (cwd)
    """
    vault_file = Path("/vault/secrets/config")
    local_env = Path(".env")
    paths = []
    if vault_file.exists():
        paths.append(str(vault_file))
    if local_env.exists():
        paths.append(str(local_env))
    return tuple(paths) if paths else None

class Settings(BaseSettings):
    # App
    APP_NAME: str = Field(default="SOA EVENTOS PERU API")
    APP_ENV: str = Field(default="dev")
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: conint(gt=0) = Field(default=8000)

    # DB (una conexión; trabajas por schemas calificados en MySQL)
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: conint(gt=0) = 3306
    DB_NAME: str  # puede ser "mysql" si el usuario tiene permisos sobre todos los schemas

    # JWT
    JWT_SECRET: str
    JWT_ALG: str = Field(default="HS256")
    JWT_EXPIRE_MIN: conint(gt=0) = Field(default=120)

    # pydantic-settings: lee Vault y .env (si existen), luego variables de entorno
    model_config = SettingsConfigDict(
        env_file=vault_or_env_path(),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("DB_PORT", mode="before")
    @classmethod
    def parse_db_port(cls, v):
        # Permite "tcp://host:port"
        if isinstance(v, str) and "://" in v:
            try:
                return int(v.split(":")[-1])
            except Exception:
                pass
        return int(v)

    @field_validator("DB_HOST", mode="before")
    @classmethod
    def parse_db_host(cls, v):
        # Normaliza "tcp://host:port" -> "host"
        if isinstance(v, str) and "://" in v:
            try:
                host_port = v.split("://", 1)[1]
                return host_port.split(":")[0]
            except Exception:
                pass
        return v

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

settings = Settings()
