from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.engine import Connection
from datetime import datetime, timedelta
import uuid

def get_intervalos_ocupados(db: Session, proveedor_id: str, inicio: datetime, fin: datetime):
    # turnos/descansos del proveedor (tipo ayuda a front; ambos ocupan)
    q_turnos = text("""
        SELECT inicio, fin, 'turno' AS fuente
        FROM ev_proveedores.calendario_proveedor
        WHERE proveedor_id=:pid AND fin > :ini AND inicio < :fin
    """)
    turnos = db.execute(q_turnos, {"pid": proveedor_id, "ini": inicio, "fin": fin}).mappings().all()

    # holds activos (status 0=hold, 1=confirmada) en la ventana
    q_holds = text("""
        SELECT inicio, fin, 'hold' AS fuente
        FROM ev_proveedores.reserva_temporal
        WHERE proveedor_id=:pid
          AND status IN (0,1)
          AND fin > :ini AND inicio < :fin
    """)
    holds = db.execute(q_holds, {"pid": proveedor_id, "ini": inicio, "fin": fin}).mappings().all()

    return [dict(r) for r in (*turnos, *holds)]

def crear_hold(db: Session, proveedor_id: str, opcion_servicio_id: str,
               inicio: datetime, fin: datetime, minutos_validez: int,
               created_by: str, correlation_id: str | None):
    # Idempotencia por (proveedor_id, correlation_id) si llega
    if correlation_id:
        q_exist = text("""
            SELECT id, status, expira_en
            FROM ev_proveedores.reserva_temporal
            WHERE proveedor_id=:pid AND correlation_id=:cid
            LIMIT 1
        """)
        row = db.execute(q_exist, {"pid": proveedor_id, "cid": correlation_id}).mappings().first()
        if row:
            return dict(row)

    hold_id = str(uuid.uuid4())
    expira_en = datetime.utcnow() + timedelta(minutes=minutos_validez)

    q_ins = text("""
        INSERT INTO ev_proveedores.reserva_temporal
          (id, proveedor_id, opcion_servicio_id, inicio, fin, status, expira_en, correlation_id, created_by)
        VALUES
          (:id, :pid, :oid, :ini, :fin, 0, :exp, :cid, :cb)
    """)
    db.execute(q_ins, {
        "id": hold_id, "pid": proveedor_id, "oid": opcion_servicio_id,
        "ini": inicio, "fin": fin, "exp": expira_en, "cid": correlation_id, "cb": created_by
    })
    db.commit()
    return {"id": hold_id, "status": 0, "expira_en": expira_en}

def listar_proveedores(db: Session, servicio_id: str, q: str | None, page: int, size: int):
    offset = (max(page,1)-1) * max(size,1)
    sql = text("""
        SELECT p.id, p.nombre, p.email, p.telefono, p.rating_prom, p.status
        FROM ev_proveedores.proveedor p
        JOIN ev_proveedores.habilidad_proveedor h ON h.proveedor_id = p.id
        WHERE h.servicio_id = :servicio_id
          AND p.status = 1 AND p.is_deleted = 0
          AND (:q IS NULL OR p.nombre LIKE CONCAT('%', :q, '%'))
        ORDER BY p.rating_prom DESC, p.nombre ASC
        LIMIT :limit OFFSET :offset
    """)
    rows = db.execute(sql, {
        "servicio_id": servicio_id,
        "q": q,
        "limit": size,
        "offset": offset
    }).mappings().all()
    return [dict(r) for r in rows]

def liberar_hold(db: Session, hold_id: str, actor_id: str | None):
    # Sólo holds activos (status=0) pasan a liberados (3); idempotente
    sql = text("""
        UPDATE ev_proveedores.reserva_temporal
           SET status = 3, expira_en = NOW(), created_by = COALESCE(created_by, :actor)
         WHERE id = :hold_id AND status = 0
    """)
    res = db.execute(sql, {"hold_id": hold_id, "actor": actor_id})
    db.commit()  # ← IMPORTANTE
    return res.rowcount  # 1 si liberó; 0 si no (ya estaba confirmada/expirada/liberada)