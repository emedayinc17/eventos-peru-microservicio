# libs/shared/ev_shared/config.py (patched)
from pathlib import Path
from urllib.parse import quote_plus
from pydantic import Field, field_validator, computed_field, conint
from pydantic_settings import BaseSettings, SettingsConfigDict

def vault_or_env_path():
    """
    Prioridad:
      1) /vault/secrets/config  (cuando corres en K8s con Vault Agent)
      2) .env del servicio      (services/<svc>/.env) — localizado automáticamente
      3) .env del working dir   (fallback para compatibilidad)
    Esto evita dependencia del directorio actual.
    """
    vault_file = Path("/vault/secrets/config")

    # Este archivo está en libs/shared/ev_shared/config.py
    # parents: [0]=config.py, [1]=ev_shared, [2]=shared, [3]=libs, [4]=<repo_root>
    repo_root = Path(__file__).resolve().parents[4]

    # Candidatos a .env por servicio
    svc_env_candidates = []
    services_dir = repo_root / "services"
    if services_dir.exists():
        for svc in services_dir.iterdir():
            if svc.is_dir():
                env_path = svc / ".env"
                if env_path.exists():
                    svc_env_candidates.append(env_path.resolve())

    # Fallback: .env del cwd
    cwd_env = Path(".env").resolve()
    if cwd_env.exists():
        svc_env_candidates.append(cwd_env)

    paths = []
    if vault_file.exists():
        paths.append(str(vault_file))

    # El primer .env que exista gana
    for p in svc_env_candidates:
        try:
            if p.exists():
                paths.append(str(p))
                break
        except Exception:
            continue

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
    JWT_EXPIRE_MIN: conint(gt=0) = Field(default=120)

    model_config = SettingsConfigDict(
        env_file=vault_or_env_path(),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @field_validator("DB_PORT", mode="before")
    @classmethod
    def parse_db_port(cls, v):
        if isinstance(v, str) and "://" in v:
            try:
                return int(v.split(":")[-1])
            except Exception:
                pass
        return int(v)

    @field_validator("DB_HOST", mode="before")
    @classmethod
    def parse_db_host(cls, v):
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
        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASS)
        host = self.DB_HOST
        port = self.DB_PORT
        name = self.DB_NAME
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"

settings = Settings()
