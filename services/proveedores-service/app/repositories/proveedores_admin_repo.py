from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid

def _uuid(): return str(uuid.uuid4())

def crear_proveedor(db: Session, nombre: str, email: str|None, telefono: str|None, status: int, actor: str|None):
    _id = _uuid()
    db.execute(text("""
      INSERT INTO ev_proveedores.proveedor (id,nombre,email,telefono,rating_prom,status,is_deleted,created_by)
      VALUES (:id,:n,:e,:t,0.0,:st,0,:cb)
    """), {"id": _id, "n": nombre, "e": email, "t": telefono, "st": status, "cb": actor})
    db.commit()
    row = db.execute(text("""
      SELECT id, nombre, email, telefono, rating_prom, status
      FROM ev_proveedores.proveedor WHERE id=:id
    """), {"id": _id}).mappings().first()
    return dict(row)

def actualizar_proveedor(db: Session, proveedor_id: str, nombre: str|None, email: str|None, telefono: str|None, status: int|None):
    sets, p = [], {"id": proveedor_id}
    if nombre is not None: sets.append("nombre=:n"); p["n"] = nombre
    if email is not None: sets.append("email=:e"); p["e"] = email
    if telefono is not None: sets.append("telefono=:t"); p["t"] = telefono
    if status is not None: sets.append("status=:st"); p["st"] = status
    if not sets:
        return 0
    res = db.execute(text(f"""
      UPDATE ev_proveedores.proveedor SET {", ".join(sets)}
      WHERE id=:id AND is_deleted=0
    """), p)
    db.commit()
    return res.rowcount

def desactivar_proveedor(db: Session, proveedor_id: str):
    res = db.execute(text("""
      UPDATE ev_proveedores.proveedor SET status=0, is_deleted=1
      WHERE id=:id AND is_deleted=0
    """), {"id": proveedor_id})
    db.commit()
    return res.rowcount

def add_habilidad(db: Session, proveedor_id: str, servicio_id: str, nivel: int):
    _id = _uuid()
    db.execute(text("""
      INSERT INTO ev_proveedores.habilidad_proveedor (id,proveedor_id,servicio_id,nivel)
      VALUES (:id,:p,:s,:n)
      ON DUPLICATE KEY UPDATE nivel=VALUES(nivel)
    """), {"id": _id, "p": proveedor_id, "s": servicio_id, "n": nivel})
    db.commit()
    return {"id": _id, "proveedor_id": proveedor_id, "servicio_id": servicio_id, "nivel": nivel}

def agregar_habilidades(db: Session, proveedor_id: str, servicio_ids: list[str]):
    for sid in servicio_ids:
        db.execute(text("""
          INSERT IGNORE INTO ev_proveedores.habilidad_proveedor (proveedor_id,servicio_id,nivel)
          VALUES (:p,:s,1)
        """), {"p": proveedor_id, "s": sid})
    db.commit()
    return {"ok": True, "proveedor_id": proveedor_id, "servicios": servicio_ids}

def quitar_habilidad(db: Session, proveedor_id: str, servicio_id: str):
    res = db.execute(text("""
      DELETE FROM ev_proveedores.habilidad_proveedor
      WHERE proveedor_id=:p AND servicio_id=:s
    """), {"p": proveedor_id, "s": servicio_id})
    db.commit()
    return res.rowcount

def add_calendario_slot(db: Session, proveedor_id: str, inicio, fin, tipo: int, actor: str|None):
    _id = _uuid()
    db.execute(text("""
      INSERT INTO ev_proveedores.calendario_proveedor (id,proveedor_id,inicio,fin,tipo,created_by)
      VALUES (:id,:p,:i,:f,:t,:cb)
    """), {"id": _id, "p": proveedor_id, "i": inicio, "f": fin, "t": tipo, "cb": actor})
    db.commit()
    return {"id": _id, "proveedor_id": proveedor_id, "inicio": str(inicio), "fin": str(fin), "tipo": tipo}
