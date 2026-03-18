from datetime import datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_campaign_command import CreateCampaignCommand
from backend.core.campaign import Campaign


class CreateCampaignHandler(RequestHandler[CreateCampaignCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateCampaignCommand) -> Campaign:
        campaign = Campaign(
            nome=command.nome,
            subject=command.subject,
            body_template=command.body_template,
            segment_filters=command.segment_filters,
            status="draft",
            tenant_id=command.tenant_id,
            criado_em=datetime.now(),
            total_sent=0,
        )
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign
