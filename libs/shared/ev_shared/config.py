# libs/shared/config.py
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field, field_validator, computed_field, conint
from pydantic_settings import BaseSettings, SettingsConfigDict


def vault_or_env_path():
    """
    Prioridad de carga de variables:
    1) /vault/secrets/config  (cuando corres en K8s con Vault Agent)
    2) ./.env                 (cuando corres local con uvicorn)
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

    # DB
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: conint(gt=0) = 3306
    DB_NAME: str

    # JWT
    JWT_SECRET: str
    JWT_ALG: str = Field(default="HS256")
    # Acepta también ACCESS_TOKEN_EXPIRE_MINUTES como alias (por Vault o .env antiguos)
    JWT_EXPIRE_MIN: conint(gt=0) = Field(
        default=120,
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # pydantic-settings: primero Vault, luego .env, y finalmente variables de entorno
    model_config = SettingsConfigDict(
        env_file=vault_or_env_path(),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---------- Normalizaciones / saneos útiles ----------

    @field_validator("DB_PORT", mode="before")
    @classmethod
    def parse_db_port(cls, v):
        # Soporta strings tipo "tcp://host:3306" o "3306"
        if isinstance(v, str):
            if "://" in v and ":" in v:
                try:
                    return int(v.split(":")[-1])
                except Exception:
                    pass
            try:
                return int(v)
            except Exception:
                pass
        return int(v)

    @field_validator("DB_HOST", mode="before")
    @classmethod
    def normalize_db_host(cls, v):
        """
        Limpia formatos problemáticos:
        - "tcp://host:3306"  -> "host"
        - "user:pass@host"   -> "host"
        - "pass@host"        -> "host"
        """
        if not isinstance(v, str):
            return v

        s = v.strip()

        # Si viene con protocolo
        if "://" in s:
            try:
                s = s.split("://", 1)[1]
            except Exception:
                pass

        # Si viene con "algo@host" (userinfo pegado por error)
        if "@" in s and "@" != s[0]:
            try:
                s = s.split("@", 1)[1]
            except Exception:
                pass

        # Quita puerto si viene pegado
        if ":" in s:
            s = s.split(":", 1)[0]

        return s.strip()

    # ---------- Propiedades derivadas ----------

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Construye un DSN seguro con URL-encoding en user/pass para
        soportar caracteres especiales (!, @, :, #, etc.).
        """
        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASS)
        host = self.DB_HOST
        port = self.DB_PORT
        name = self.DB_NAME
        return (
            f"mysql+pymysql://{user}:{password}"
            f"@{host}:{port}/{name}?charset=utf8mb4"
        )


settings = Settings()
