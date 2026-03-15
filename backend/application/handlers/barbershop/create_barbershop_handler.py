from sqlalchemy.orm import Session

from backend.application.commands.create_barbershop_command import CreateBarbershopCommand
from backend.core.barbershop import Barbershop
from backend.core.exceptions import NotFoundError
from backend.core.tenant import Tenant
from backend.core.tenant_slug import slugify_tenant_name
from backend.core.user import User
from diator.requests import RequestHandler


class CreateBarbershopHandler(RequestHandler[CreateBarbershopCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    def _build_unique_tenant_slug(self, name: str) -> str:
        base_slug = slugify_tenant_name(name)
        slug = base_slug
        counter = 2

        while self.db.query(Tenant).filter(Tenant.slug == slug).first() is not None:
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    async def handle(self, command: CreateBarbershopCommand):
        owner_user = self.db.query(User).filter(User.id == command.owner_user_id).first()
        if owner_user is None:
            raise NotFoundError("Owner user not found")

        tenant = Tenant(
            nome=command.name,
            slug=self._build_unique_tenant_slug(command.name),
        )
        self.db.add(tenant)
        self.db.flush()

        barbershop = Barbershop(
            nome=command.name,
            owner_user_id=command.owner_user_id,
            tenant_id=tenant.id,
        )
        self.db.add(barbershop)
        self.db.commit()
        self.db.refresh(barbershop)
        return barbershop
