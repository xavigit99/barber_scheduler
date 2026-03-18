import logging
import os
import uuid
from datetime import datetime

from diator.requests import RequestHandler
from sqlalchemy.orm import Session

from backend.application.commands.create_invoice_command import CreateInvoiceCommand
from backend.core.appointment import Appointment
from backend.core.client import Client
from backend.core.exceptions import NotFoundError
from backend.core.invoice import Invoice
from backend.core.service import Service
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class CreateInvoiceHandler(RequestHandler[CreateInvoiceCommand, object]):

    def __init__(self, db: Session):
        self.db = db

    async def handle(self, command: CreateInvoiceCommand) -> Invoice:
        repo = BaseRepository(Appointment, self.db, tenant_id=command.tenant_id)
        appointment = repo.get(command.appointment_id)
        if appointment is None:
            raise NotFoundError("Appointment not found")

        service = (
            self.db.query(Service)
            .filter(Service.id == appointment.service_id, Service.deleted.is_(False))
            .first()
        )
        client = (
            self.db.query(Client)
            .filter(Client.id == appointment.client_id, Client.deleted.is_(False))
            .first()
        )

        api_key = os.getenv("INVOICEXPRESS_API_KEY", "")
        account_name = os.getenv("INVOICEXPRESS_ACCOUNT_NAME", "")

        invoice_url = None
        invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"

        if api_key and account_name:
            try:
                import httpx

                # InvoiceXpress simplified invoice creation
                url = f"https://{account_name}.app.invoicexpress.com/invoices.json"
                payload = {
                    "invoice": {
                        "date": datetime.now().strftime("%d/%m/%Y"),
                        "due_date": datetime.now().strftime("%d/%m/%Y"),
                        "client": {
                            "name": client.nome if client else "Unknown",
                            "email": client.email if client else "",
                        },
                        "items": [
                            {
                                "name": service.nome if service else "Service",
                                "unit_price": str(service.preco) if service else "0",
                                "quantity": "1",
                            },
                        ],
                    },
                }
                resp = httpx.post(
                    url,
                    json=payload,
                    params={"api_key": api_key},
                    headers={"Content-Type": "application/json"},
                    timeout=15,
                )
                if resp.status_code in (200, 201):
                    data = resp.json()
                    invoice_number = str(data.get("invoice", {}).get("id", invoice_number))
                    invoice_url = data.get("invoice", {}).get("permalink")
                    logger.info("InvoiceXpress invoice created: %s", invoice_number)
                else:
                    logger.warning(
                        "InvoiceXpress returned %s: %s", resp.status_code, resp.text,
                    )
            except Exception:
                logger.warning("InvoiceXpress API call failed", exc_info=True)

        invoice = Invoice(
            appointment_id=command.appointment_id,
            tenant_id=command.tenant_id,
            invoice_number=invoice_number,
            invoice_url=invoice_url,
            status="sent" if invoice_url else "draft",
            criado_em=datetime.now(),
        )
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice
