from app.database.models.audit import AuditLog


def create_audit_log(db, *, user_id, entity_type: str, entity_id: str, action: str, old_value=None, new_value=None, ip_address=None) -> AuditLog:
    log = AuditLog(
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
    )
    db.add(log)
    db.flush()
    db.refresh(log)
    return log
