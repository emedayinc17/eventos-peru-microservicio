from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid

def crear_pedido(db: Session, cliente_id: str, tipo_evento_id: str,
                 fecha_evento, hora_inicio, hora_fin, ubicacion: str,
                 moneda: str, request_id: str | None, created_by: str, correlation_id: str | None):
    if request_id:
        row = db.execute(text("SELECT id FROM ev_contratacion.pedido_evento WHERE request_id=:rid LIMIT 1"),
                         {"rid": request_id}).first()
        if row:
            return dict(db.execute(text("""
                SELECT id, cliente_id, tipo_evento_id, fecha_evento, hora_inicio, hora_fin,
                       ubicacion, monto_total, moneda, status
                  FROM ev_contratacion.pedido_evento WHERE id=:id
            """), {"id": row[0]}).mappings().first())

    pid = str(uuid.uuid4())
    db.execute(text("""
        INSERT INTO ev_contratacion.pedido_evento
          (id, cliente_id, tipo_evento_id, fecha_evento, hora_inicio, hora_fin, ubicacion,
           monto_total, moneda, status, correlation_id, request_id, created_by)
        VALUES
          (:id, :cli, :te, :fe, :hi, :hf, :ubi, 0.00, :mon, 0, :cid, :rid, :cb)
    """), {
        "id": pid, "cli": cliente_id, "te": tipo_evento_id, "fe": fecha_evento,
        "hi": hora_inicio, "hf": hora_fin, "ubi": ubicacion, "mon": moneda,
        "cid": correlation_id, "rid": request_id, "cb": created_by
    })
    db.commit()
    return dict(db.execute(text("""
        SELECT id, cliente_id, tipo_evento_id, fecha_evento, hora_inicio, hora_fin,
               ubicacion, monto_total, moneda, status
          FROM ev_contratacion.pedido_evento WHERE id=:id
    """), {"id": pid}).mappings().first())

def add_item(db: Session, pedido_id: str, tipo_item: int, referencia_id: str,
             cantidad: int, precio_unit: float, created_by: str):
    iid = str(uuid.uuid4())
    precio_total = round(precio_unit * cantidad, 2)

    db.execute(text("""
        INSERT INTO ev_contratacion.item_pedido_evento
          (id, pedido_id, tipo_item, referencia_id, cantidad, precio_unit, precio_total, created_at, created_by)
        VALUES
          (:id, :pid, :ti, :ref, :cant, :pu, :pt, NOW(), :cb)
    """), {
        "id": iid, "pid": pedido_id, "ti": tipo_item, "ref": referencia_id,
        "cant": cantidad, "pu": precio_unit, "pt": precio_total, "cb": created_by
    })

    db.execute(text("""
        UPDATE ev_contratacion.pedido_evento pe
        JOIN (
            SELECT COALESCE(SUM(precio_total),0) AS s
            FROM ev_contratacion.item_pedido_evento
            WHERE pedido_id=:pid
        ) x ON 1=1
        SET pe.monto_total = x.s
        WHERE pe.id=:pid
    """), {"pid": pedido_id})
    db.commit()

    return {
        "id": iid, "pedido_id": pedido_id, "tipo_item": tipo_item,
        "referencia_id": referencia_id, "cantidad": cantidad,
        "precio_unit": float(precio_unit), "precio_total": float(precio_total)
    }

def _exists(db: Session, sql_txt: str, params: dict) -> bool:
    return bool(db.execute(text(sql_txt), params).scalar())

def chk_solape(db: Session, proveedor_id: str, inicio: str, fin: str) -> bool:
    sql_res = """
        SELECT EXISTS(
          SELECT 1 FROM ev_contratacion.reserva r
           WHERE r.proveedor_id=:prov AND r.status IN (0,1)
             AND r.inicio < :fin AND r.fin > :inicio
        )
    """
    sql_hold = """
        SELECT EXISTS(
          SELECT 1 FROM ev_proveedores.reserva_temporal h
           WHERE h.proveedor_id=:prov AND h.status IN (0,1)
             AND h.inicio < :fin AND h.fin > :inicio
        )
    """
    sql_desc = """
        SELECT EXISTS(
          SELECT 1 FROM ev_proveedores.calendario_proveedor c
           WHERE c.proveedor_id=:prov AND c.tipo=2
             AND c.inicio < :fin AND c.fin > :inicio
        )
    """
    p = {"prov": proveedor_id, "inicio": inicio, "fin": fin}
    return _exists(db, sql_res, p) or _exists(db, sql_hold, p) or _exists(db, sql_desc, p)

def crear_reserva_con_chk(db: Session, item_pedido_id: str, proveedor_id: str,
                          inicio: str, fin: str, hold_id: str | None, actor_id: str | None):
    if chk_solape(db, proveedor_id, inicio, fin):
        return None, "conflict"

    rid = str(uuid.uuid4())
    db.execute(text("""
        INSERT INTO ev_contratacion.reserva
           (id, item_pedido_id, proveedor_id, inicio, fin, status, hold_id, created_at, created_by)
        VALUES
           (:id, :iid, :pid, :ini, :fin, 0, :hid, NOW(), :actor)
    """), {
        "id": rid, "iid": item_pedido_id, "pid": proveedor_id,
        "ini": inicio, "fin": fin, "hid": hold_id, "actor": actor_id
    })

    # Consume el hold si aplica (status=1=confirmada)
    if hold_id:
        db.execute(text("""
            UPDATE ev_proveedores.reserva_temporal
               SET status = 1
             WHERE id = :hid AND status = 0
        """), {"hid": hold_id})

    db.commit()

    row = db.execute(text("""
        SELECT id, item_pedido_id, proveedor_id, inicio, fin, status, hold_id
          FROM ev_contratacion.reserva
         WHERE id=:id
    """), {"id": rid}).mappings().first()
    return dict(row), None

def confirmar_pedido(db: Session, pedido_id: str, actor_id: str | None):
    ok = db.execute(text("""
        SELECT NOT EXISTS (
          SELECT 1
          FROM ev_contratacion.item_pedido_evento i
          WHERE i.pedido_id = :pid
          AND NOT EXISTS (
            SELECT 1 FROM ev_contratacion.reserva r
            WHERE r.item_pedido_id = i.id AND r.status = 1
          )
        ) AS ok
    """), {"pid": pedido_id}).scalar()
    if not ok:
        return 0
    res = db.execute(text("""
        UPDATE ev_contratacion.pedido_evento
           SET status = 1, updated_by = :actor
         WHERE id = :pid AND status = 0
    """), {"pid": pedido_id, "actor": actor_id})
    db.commit()
    return res.rowcount

def cancelar_pedido(db: Session, pedido_id: str, actor_id: str | None, motivo: str | None):
    upd_ped = db.execute(text("""
        UPDATE ev_contratacion.pedido_evento
           SET status = 2, updated_by=:actor
         WHERE id=:pid AND status IN (0,1)
    """), {"pid": pedido_id, "actor": actor_id})

    db.execute(text("""
        UPDATE ev_contratacion.reserva
           SET status = 3
         WHERE item_pedido_id IN (
           SELECT id FROM ev_contratacion.item_pedido_evento WHERE pedido_id=:pid
         ) AND status IN (0,1)
    """), {"pid": pedido_id})

    db.execute(text("""
        UPDATE ev_proveedores.reserva_temporal
           SET status = 3
         WHERE id IN (
           SELECT r.hold_id FROM ev_contratacion.reserva r
           JOIN ev_contratacion.item_pedido_evento i ON i.id=r.item_pedido_id
          WHERE i.pedido_id=:pid AND r.hold_id IS NOT NULL
         )
    """), {"pid": pedido_id})

    db.execute(text("""
        INSERT INTO ev_iam.evento_audit(id, entidad, entidad_id, accion, actor_id, metadata)
        VALUES(UUID(),'pedido_evento', :pid, 'CANCELAR', :actor, JSON_OBJECT('motivo', :motivo))
    """), {"pid": pedido_id, "actor": actor_id, "motivo": motivo})

    db.commit()
    return upd_ped.rowcount

def ejecutar_pedido(db: Session, pedido_id: str, actor_id: str | None):
    res = db.execute(text("""
        UPDATE ev_contratacion.pedido_evento
           SET status = 3, updated_by=:actor
         WHERE id=:pid AND status = 1
    """), {"pid": pedido_id, "actor": actor_id})
    db.commit()
    return res.rowcount
