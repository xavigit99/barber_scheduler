from sqlalchemy.orm import Session

from backend.core.client import Client
from backend.core.user import User


def get_client_profile_for_user(
    db: Session,
    *,
    user_id: int,
    tenant_id: int | None,
) -> Client | None:
    query = db.query(Client).filter(Client.user_id == user_id, Client.deleted.is_(False))
    if tenant_id is not None:
        query = query.filter(Client.tenant_id == tenant_id)
    return query.order_by(Client.id.desc()).first()


def get_or_create_client_profile_for_user(
    db: Session,
    *,
    user_id: int,
    tenant_id: int,
) -> Client | None:
    existing = get_client_profile_for_user(db, user_id=user_id, tenant_id=tenant_id)
    if existing is not None:
        return existing

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None

    seed_profile = get_client_profile_for_user(db, user_id=user_id, tenant_id=None)
    client = Client(
        nome=seed_profile.nome if seed_profile is not None else user.username,
        email=user.email,
        telefone=seed_profile.telefone if seed_profile is not None else None,
        data_nascimento=seed_profile.data_nascimento if seed_profile is not None else None,
        tenant_id=tenant_id,
        user_id=user_id,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client
