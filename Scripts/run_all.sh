
# scripts/run_all.sh
set -euo pipefail

start_one () {
  SVC="$1"; PORT="$2"
  APPDIR="services/$SVC"
  ENVFILE="$APPDIR/.env"
  export PYTHONPATH="$PWD/libs/shared:$PWD/$APPDIR"
  CMD="uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload --app-dir $APPDIR"
  if [ -f "$ENVFILE" ]; then
    CMD="$CMD --env-file $ENVFILE"
  fi
  echo ">>> $SVC on :$PORT"
  bash -lc "$CMD" &
}

start_one iam-service 8010
start_one catalogo-service 8020
start_one proveedores-service 8030
start_one contratacion-service 8040

wait
