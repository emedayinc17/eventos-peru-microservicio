# Patch: Local .env + Vault-ready start (Eventos Perú)

## Qué incluye
- `libs/shared/ev_shared/config.py` con `vault_or_env_path()` robusto:
  Prioriza `/vault/secrets/config`, luego `services/<svc>/.env`, luego `.env` del cwd.
- Shim de seguridad en cada servicio (`app/core/security.py`) para reutilizar la lib compartida.
- Snippet a insertar al inicio de `app/main.py` de cada servicio para cargar settings temprano.
- `scripts/run_all.ps1` y `scripts/run_all.sh` para levantar los 4 servicios en local.

## Cómo aplicar
1. Copia los archivos del ZIP en la raíz del proyecto (permitiendo sobrescribir rutas existentes).
2. En cada servicio, agrega arriba de `services/<svc>/app/main.py` el contenido de:
   `services/<svc>/app/main.prepend.py` (ES UNA INSERCIÓN, no borres tu main).
   Quedará así al tope:
   ```python
   from ev_shared.config import settings  # noqa: F401
   ```
3. Asegúrate que en `services/<svc>/.env` estén definidos: `DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME` y `JWT_SECRET` (mismo valor en todos).
4. Opcional: en `services/<svc>/app/core/deps.py` corrige el import a:
   ```python
   from ev_shared.security import decode_jwt
   ```

## Ejecutar en local (Windows PowerShell)
```powershell
scriptsun_all.ps1
```

## Ejecutar en local (Linux/Mac)
```bash
chmod +x scripts/run_all.sh
./scripts/run_all.sh
```

## Notas
- En Kubernetes con Vault Agent, el archivo `/vault/secrets/config` tendrá prioridad automáticamente.
- Si prefieres no insertar el snippet en `main.py`, también puedes ejecutar con `--env-file services/<svc>/.env`.
- Si ves `ValidationError: DB_NAME missing`, revisa que cada `.env` de servicio tenga su `DB_NAME` correcto.
