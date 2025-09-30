from sqlalchemy.orm import Session
from sqlalchemy import text

def get_tipos_evento(db: Session):
    q = text("""SELECT id, nombre, descripcion, status
                FROM ev_catalogo.tipo_evento
                WHERE is_deleted=0 AND status=1""")
    return db.execute(q).mappings().all()

def get_servicios(db: Session, tipo_evento_id: str | None):
    if tipo_evento_id:
        q = text("""SELECT id, nombre, descripcion, tipo_evento_id, status
                    FROM ev_catalogo.servicio
                    WHERE is_deleted=0 AND status=1 AND tipo_evento_id=:te""")
        return db.execute(q, {"te": tipo_evento_id}).mappings().all()
    q = text("""SELECT id, nombre, descripcion, tipo_evento_id, status
                FROM ev_catalogo.servicio
                WHERE is_deleted=0 AND status=1""")
    return db.execute(q).mappings().all()

def get_opciones_con_precio_vigente(db: Session, servicio_id: str | None):
    if servicio_id:
        q = text("""SELECT opcion_id, servicio_id, nombre, detalles, moneda, monto
                    FROM ev_catalogo.v_opcion_con_precio_vigente
                    WHERE servicio_id=:sid""")
        return db.execute(q, {"sid": servicio_id}).mappings().all()
    q = text("""SELECT opcion_id, servicio_id, nombre, detalles, moneda, monto
                FROM ev_catalogo.v_opcion_con_precio_vigente""")
    return db.execute(q).mappings().all()

def get_paquetes_detalle(db: Session):
    q = text("""SELECT paquete_id, codigo, nombre, descripcion, status,
                       opcion_servicio_id, cantidad, moneda, monto
                FROM ev_paquetes.v_paquete_detalle""")
    return db.execute(q).mappings().all()
