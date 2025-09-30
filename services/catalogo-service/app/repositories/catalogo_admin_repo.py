from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid, json

def _uuid(): return str(uuid.uuid4())

# ========= TIPOS / SERVICIOS / OPCIONES / PRECIOS OPCION =========

def crear_tipo_evento(db: Session, nombre: str, descripcion: str|None, actor: str|None):
    _id = _uuid()
    db.execute(text("""
      INSERT INTO ev_catalogo.tipo_evento (id,nombre,descripcion,status,created_by)
      VALUES (:id,:n,:d,1,:cb)
    """), {"id": _id, "n": nombre, "d": descripcion, "cb": actor})
    db.commit()
    return {"id": _id, "nombre": nombre, "descripcion": descripcion, "status": 1}

def crear_servicio(db: Session, nombre: str, descripcion: str|None, tipo_evento_id: str, actor: str|None):
    _id = _uuid()
    db.execute(text("""
      INSERT INTO ev_catalogo.servicio (id,nombre,descripcion,tipo_evento_id,status,created_by)
      VALUES (:id,:n,:d,:te,1,:cb)
    """), {"id": _id, "n": nombre, "d": descripcion, "te": tipo_evento_id, "cb": actor})
    db.commit()
    return {"id": _id, "nombre": nombre, "descripcion": descripcion, "tipo_evento_id": tipo_evento_id, "status": 1}

def crear_opcion(db: Session, servicio_id: str, nombre: str, detalles, actor: str|None):
    _id = _uuid()
    db.execute(text("""
      INSERT INTO ev_catalogo.opcion_servicio (id,servicio_id,nombre,detalles,status,created_by)
      VALUES (:id,:sid,:n,:det,1,:cb)
    """), {"id": _id, "sid": servicio_id, "n": nombre,
           "det": json.dumps(detalles) if detalles is not None else None, "cb": actor})
    db.commit()
    return {"id": _id, "servicio_id": servicio_id, "nombre": nombre, "detalles": detalles, "status": 1}

def crear_precio_opcion(db: Session, opcion_id: str, moneda: str, monto: float, desde, hasta, actor: str|None):
    _id = _uuid()
    db.execute(text("""
      INSERT INTO ev_catalogo.precio_servicio (id,opcion_servicio_id,moneda,monto,vigente_desde,vigente_hasta,created_by)
      VALUES (:id,:oid,:mon,:m,:vd,:vh,:cb)
    """), {"id": _id, "oid": opcion_id, "mon": moneda, "m": monto,
           "vd": desde, "vh": hasta, "cb": actor})
    db.commit()
    return {"id": _id, "opcion_servicio_id": opcion_id, "moneda": moneda,
            "monto": float(monto), "vigente_desde": str(desde),
            "vigente_hasta": (str(hasta) if hasta else None)}

# ========= PAQUETES (por decisión: ev_paquetes) =========

SCHEMA_PQ = "ev_paquetes"  # cambia a "ev_catalogo" si unificas

def listar_paquetes_admin(db: Session, q: str|None, page: int, size: int):
    offset = (max(page,1)-1) * max(size,1)
    params = {"limit": size, "offset": offset}
    where = "WHERE 1=1"
    if q:
        where += " AND (p.codigo LIKE CONCAT('%',:q,'%') OR p.nombre LIKE CONCAT('%',:q,'%'))"
        params["q"] = q

    rows = db.execute(text(f"""
      SELECT p.id, p.codigo, p.nombre, p.descripcion, p.status
      FROM {SCHEMA_PQ}.paquete p
      {where}
      ORDER BY p.codigo ASC
      LIMIT :limit OFFSET :offset
    """), params).mappings().all()
    total = db.execute(text(f"SELECT COUNT(*) FROM {SCHEMA_PQ}.paquete p {where}"), params).scalar() or 0
    return [dict(r) for r in rows], int(total)

def crear_paquete(db: Session, codigo: str, nombre: str, descripcion: str|None, actor: str|None):
    # evita duplicar código
    exists = db.execute(text(f"SELECT 1 FROM {SCHEMA_PQ}.paquete WHERE codigo=:c LIMIT 1"), {"c": codigo}).scalar()
    if exists:
        return None, "dup"

    _id = _uuid()
    db.execute(text(f"""
      INSERT INTO {SCHEMA_PQ}.paquete (id,codigo,nombre,descripcion,status,created_by)
      VALUES (:id,:c,:n,:d,1,:cb)
    """), {"id": _id, "c": codigo, "n": nombre, "d": descripcion, "cb": actor})
    db.commit()
    row = db.execute(text(f"""
      SELECT id, codigo, nombre, descripcion, status
      FROM {SCHEMA_PQ}.paquete WHERE id=:id
    """), {"id": _id}).mappings().first()
    return dict(row), None

def actualizar_paquete(db: Session, paquete_id: str, nombre: str|None, descripcion: str|None, status: int|None):
    sets, p = [], {"id": paquete_id}
    if nombre is not None: sets.append("nombre=:nom"); p["nom"] = nombre
    if descripcion is not None: sets.append("descripcion=:des"); p["des"] = descripcion
    if status is not None: sets.append("status=:st"); p["st"] = status
    if not sets:
        return 0
    res = db.execute(text(f"""
      UPDATE {SCHEMA_PQ}.paquete SET {", ".join(sets)}
      WHERE id=:id
    """), p)
    db.commit()
    return res.rowcount

def add_item_paquete(db: Session, paquete_id: str, opcion_servicio_id: str, cantidad: int):
    _id = _uuid()
    db.execute(text(f"""
      INSERT INTO {SCHEMA_PQ}.item_paquete (id,paquete_id,opcion_servicio_id,cantidad)
      VALUES (:id,:pid,:oid,:cant)
    """), {"id": _id, "pid": paquete_id, "oid": opcion_servicio_id, "cant": cantidad})
    db.commit()
    row = db.execute(text(f"""
      SELECT id, paquete_id, opcion_servicio_id, cantidad
      FROM {SCHEMA_PQ}.item_paquete WHERE id=:id
    """), {"id": _id}).mappings().first()
    return dict(row)

def eliminar_item_paquete(db: Session, paquete_id: str, item_id: str):
    res = db.execute(text(f"""
      DELETE FROM {SCHEMA_PQ}.item_paquete
      WHERE id=:iid AND paquete_id=:pid
    """), {"iid": item_id, "pid": paquete_id})
    db.commit()
    return res.rowcount

def crear_precio_paquete(db: Session, paquete_id: str, moneda: str, monto: float, desde, hasta, actor: str|None):
    _id = _uuid()
    db.execute(text(f"""
      INSERT INTO {SCHEMA_PQ}.precio_paquete (id,paquete_id,moneda,monto,vigente_desde,vigente_hasta,created_by)
      VALUES (:id,:pid,:mon,:m,:vd,:vh,:cb)
    """), {"id": _id, "pid": paquete_id, "mon": moneda, "m": monto,
           "vd": desde, "vh": hasta, "cb": actor})
    db.commit()
    row = db.execute(text(f"""
      SELECT id, paquete_id, moneda, monto, vigente_desde, vigente_hasta
      FROM {SCHEMA_PQ}.precio_paquete WHERE id=:id
    """), {"id": _id}).mappings().first()
    return {
        "id": row["id"],
        "paquete_id": row["paquete_id"],
        "moneda": row["moneda"],
        "monto": float(row["monto"]),
        "vigente_desde": str(row["vigente_desde"]),
        "vigente_hasta": (str(row["vigente_hasta"]) if row["vigente_hasta"] else None)
    }
