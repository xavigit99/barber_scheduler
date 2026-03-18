import json
import logging
from datetime import datetime, timedelta

from diator.requests import RequestHandler
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.application.commands.send_campaign_command import SendCampaignCommand
from backend.core.appointment import Appointment
from backend.core.campaign import Campaign
from backend.core.client import Client
from backend.core.exceptions import NotFoundError, ValidationError
from backend.core.notifications import get_notification_service
from backend.core.service import Service
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class SendCampaignHandler(RequestHandler[SendCampaignCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: SendCampaignCommand) -> Campaign:
        repo = BaseRepository(Campaign, self.db, tenant_id=command.tenant_id)
        campaign = repo.get(command.campaign_id)
        if campaign is None:
            raise NotFoundError("Campaign not found")
        if campaign.status == "sent":
            raise ValidationError("Campaign already sent")

        # Parse segment filters and build matching client list
        filters = json.loads(campaign.segment_filters)
        clients = self._get_segmented_clients(command.tenant_id, filters)

        # Send emails
        notifier = get_notification_service()
        sent_count = 0
        for client in clients:
            try:
                body = campaign.body_template.replace("{{nome}}", client.nome)
                notifier.send_campaign(
                    client_name=client.nome,
                    client_email=client.email,
                    subject=campaign.subject,
                    body=body,
                )
                sent_count += 1
            except Exception:
                logger.warning(
                    "Failed to send campaign email to %s", client.email, exc_info=True,
                )

        campaign.status = "sent"
        campaign.enviado_em = datetime.now()
        campaign.total_sent = sent_count
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def _get_segmented_clients(
        self, tenant_id: int | None, filters: dict,
    ) -> list[Client]:
        """Build client list by applying segment filters — mirrors F32 logic."""
        query = (
            self.db.query(Client)
            .filter(Client.deleted.is_(False))
        )
        if tenant_id is not None:
            query = query.filter(Client.tenant_id == tenant_id)

        inactive_days = filters.get("inactive_days")
        if inactive_days is not None:
            cutoff = datetime.now() - timedelta(days=int(inactive_days))
            active_client_ids = (
                self.db.query(Appointment.client_id)
                .filter(
                    Appointment.deleted.is_(False),
                    Appointment.start_at >= cutoff,
                )
                .distinct()
                .subquery()
            )
            query = query.filter(Client.id.notin_(active_client_ids))

        min_spend = filters.get("min_spend")
        if min_spend is not None:
            high_spend_ids = (
                self.db.query(Appointment.client_id)
                .join(Service, Service.id == Appointment.service_id)
                .filter(Appointment.deleted.is_(False))
                .group_by(Appointment.client_id)
                .having(func.sum(Service.preco) >= float(min_spend))
                .subquery()
            )
            query = query.filter(Client.id.in_(high_spend_ids))

        service_id = filters.get("service_id")
        if service_id is not None:
            service_client_ids = (
                self.db.query(Appointment.client_id)
                .filter(
                    Appointment.deleted.is_(False),
                    Appointment.service_id == int(service_id),
                )
                .distinct()
                .subquery()
            )
            query = query.filter(Client.id.in_(service_client_ids))

        has_birthday = filters.get("has_birthday_this_month")
        if has_birthday:
            current_month = datetime.now().month
            query = query.filter(
                func.extract("month", Client.data_nascimento) == current_month,
            )

        return query.all()
