from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class GetInvoiceQuery(Request):
    invoice_id: int
    tenant_id: int
