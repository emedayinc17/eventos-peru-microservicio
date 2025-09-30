# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, computed_field, conint
import os
from pathlib import Path

def vault_or_env_path():
    """
    Si existe el file inyectado por Vault Agent (/vault/secrets/config),
    úsalo primero. Si no, usa .env local.
    """
    vault_file = Path("/vault/secrets/config")
    local_env = Path(".env")
    # Puedes añadir otro fallback como "app/.env" si tu estructura lo requiere
    paths = []
    if vault_file.exists():
        paths.append(str(vault_file))
    if local_env.exists():
        paths.append(str(local_env))
    # Si ninguno existe, pydantic-settings solo leerá del entorno del proceso.
    return tuple(paths) if paths else None

class Settings(BaseSettings):
    # App
    APP_NAME: str = Field(default="SOA EVENTOS PERU API")
    APP_ENV: str = Field(default="dev")
    APP_HOST: str = Field(default="0.0.0.0")
    APP_PORT: conint(gt=0) = Field(default=8000)

    # DB (una conexión; trabajas por schemas lógicos en MySQL)
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: conint(gt=0) = 3306  # puede venir "tcp://host:port" → lo normalizamos abajo
    DB_NAME: str  # puedes usar "mysql" o el schema principal

    # JWT
    JWT_SECRET: str
    JWT_ALG: str = Field(default="HS256")
    JWT_EXPIRE_MIN: conint(gt=0) = Field(default=120)

    # Config de carga de variables
    # Nota: env_file acepta tuple de rutas; si es None, solo environment vars.
    model_config = SettingsConfigDict(
        env_file=vault_or_env_path(),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Normaliza cuando Vault entrega "tcp://host:port"
    @field_validator("DB_PORT", mode="before")
    @classmethod
    def parse_db_port(cls, v):
        if isinstance(v, str) and "://" in v:
            # Ej: "tcp://mysql.svc.cluster.local:3306"
            try:
                return int(v.split(":")[-1])
            except Exception:
                pass
        return int(v)

    # (Opcional) si también quieres normalizar DB_HOST viniendo "tcp://host:port"
    @field_validator("DB_HOST", mode="before")
    @classmethod
    def parse_db_host(cls, v):
        if isinstance(v, str) and "://" in v:
            # Ej: "tcp://mysql.svc.cluster.local:3306" -> "mysql.svc.cluster.local"
            try:
                host_port = v.split("://", 1)[1]
                return host_port.split(":")[0]
            except Exception:
                pass
        return v

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # PyMySQL
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

settings = Settings()
