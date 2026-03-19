from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BarberBase(BaseModel):
    nome: str
    email: str
    telefone: str | None = None


class BarberCreate(BarberBase):
    tenant_id: int


class BarberUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None
    tenant_id: int | None = None


class BarberResponse(BarberBase):
    id: int

    tenant_id: int

    class Config:
        from_attributes = True


class BarbershopBase(BaseModel):
    nome: str


class BarbershopCreate(BarbershopBase):
    pass


class BarbershopUpdate(BaseModel):
    nome: str | None = None


class BarbershopResponse(BarbershopBase):
    id: int
    owner_user_id: int
    tenant_id: int

    class Config:
        from_attributes = True


class BarberAvailabilityBase(BaseModel):
    dia_semana: int = Field(ge=0, le=6)
    hora_inicio: time
    hora_fim: time


class BarberAvailabilityCreate(BarberAvailabilityBase):
    pass


class BarberAvailabilityUpdate(BaseModel):
    dia_semana: int | None = Field(default=None, ge=0, le=6)
    hora_inicio: time | None = None
    hora_fim: time | None = None


class BarberAvailabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    barber_id: int
    dia_semana: int = Field(alias="weekday")
    hora_inicio: time = Field(alias="start_time")
    hora_fim: time = Field(alias="end_time")


class BarberBlockBase(BaseModel):
    tipo: str
    inicio: datetime
    fim: datetime
    motivo: str | None = None


class BarberBlockCreate(BarberBlockBase):
    pass


class BarberBlockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    barber_id: int
    tipo: str = Field(alias="kind")
    inicio: datetime = Field(alias="start_at")
    fim: datetime = Field(alias="end_at")
    motivo: str | None = Field(default=None, alias="reason")


class AvailableSlotResponse(BaseModel):
    inicio: datetime
    fim: datetime


class AvailableSlotsResponse(BaseModel):
    barber_id: int
    service_id: int
    data: date
    timezone: str
    slots: list[AvailableSlotResponse]


class AvailableDatesResponse(BaseModel):
    barber_id: int
    service_id: int
    start_date: date
    end_date: date
    timezone: str
    dates: list[date]


class AppointmentCreateRequest(BaseModel):
    barber_id: int
    client_id: int
    service_id: int
    data_inicio: datetime
    resource_id: int | None = None  # F38 — optional room/resource


class AppointmentRescheduleRequest(BaseModel):
    nova_data_inicio: datetime


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    barber_id: int
    client_id: int
    service_id: int
    start_at: datetime
    end_at: datetime
    created_at: datetime
    updated_at: datetime
    status: str = "pending"
    confirmed_at: datetime | None = None
    group_id: str | None = None


class ClientBase(BaseModel):
    nome: str
    email: str
    telefone: str | None = None
    data_nascimento: date | None = None


class ClientCreate(ClientBase):
    tenant_id: int


class ClientUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None
    tenant_id: int | None = None
    data_nascimento: date | None = None


class ClientResponse(ClientBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True


class ServiceBase(BaseModel):
    nome: str
    duracao_minutos: int = Field(gt=0)
    preco: float = Field(ge=0)
    max_capacity: int = Field(default=1, ge=1)


class ServiceCreate(ServiceBase):
    tenant_id: int


class ServiceUpdate(BaseModel):
    nome: str | None = None
    duracao_minutos: int | None = Field(default=None, gt=0)
    preco: float | None = Field(default=None, ge=0)
    tenant_id: int | None = None
    max_capacity: int | None = Field(default=None, ge=1)


class ServiceResponse(ServiceBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: str
    role: str  # comma-separated roles, e.g. "barber,client"


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserCreateRequest(UserBase):
    password: str = Field(min_length=8)


class ClientRegisterRequest(BaseModel):
    username: str
    email: str
    password: str = Field(min_length=8)
    nome: str


class BarberRegisterRequest(BaseModel):
    username: str
    email: str
    password: str = Field(min_length=8)
    nome: str
    telefone: str | None = None
    tenant_id: int


class BootstrapAdminRequest(BaseModel):
    username: str
    email: str
    password: str = Field(min_length=8)


class AuthLoginRequest(BaseModel):
    username: str
    password: str = Field(min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class MembershipCreate(BaseModel):
    barber_id: int
    role: str


class MembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    barber_id: int
    barbershop_id: int
    role: str


class PublicAppointmentCreateRequest(BaseModel):
    barber_id: int
    service_id: int
    start_at: datetime
    tenant_id: int
    client_name: str = Field(min_length=1, max_length=200)
    client_email: EmailStr
    client_phone: str | None = Field(default=None, max_length=30)


class PublicAppointmentResponse(BaseModel):
    id: int
    barber_id: int
    client_id: int
    service_id: int
    start_at: datetime
    end_at: datetime
    client_name: str
    client_email: str


ClienteCreate = ClientCreate
ClienteUpdate = ClientUpdate
ClienteResponse = ClientResponse


class TenantStatsResponse(BaseModel):
    barbers: int
    clients: int
    services: int
    appointments_month: int
    cancelled_month: int
    revenue_month: float


class PurgeRequest(BaseModel):
    entity: str
    older_than_days: int


class PurgeResponse(BaseModel):
    entity: str
    purged_count: int


class TenantExportResponse(BaseModel):
    tenant_id: int
    exported_at: str
    barbers: list[dict]
    clients: list[dict]
    services: list[dict]
    appointments: list[dict]
    memberships: list[dict]


class FeedbackCreate(BaseModel):
    appointment_id: int
    rating: int = Field(ge=1, le=5)
    comentario: str | None = Field(default=None, max_length=2000)


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    appointment_id: int
    client_id: int
    barber_id: int
    tenant_id: int
    rating: int
    comentario: str | None
    created_at: datetime


class PublicFeedbackResponse(BaseModel):
    """Public-safe subset — omits internal IDs (client_id, appointment_id, tenant_id)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    barber_id: int
    rating: int
    comentario: str | None
    created_at: datetime


# ── Webhooks ─────────────────────────────────────────────────────────────────


class WebhookCreate(BaseModel):
    url: str
    secret: str
    events: list[str]


class WebhookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    url: str
    events: list[str]
    created_at: datetime


# ── Recurring Appointments ───────────────────────────────────────────────────


class RecurringAppointmentRequest(BaseModel):
    barber_id: int
    client_id: int
    service_id: int
    data_inicio: datetime
    recurrence: Literal["weekly", "biweekly"]
    count: int = Field(ge=1, le=12)


# ── Group Appointments (F27) ─────────────────────────────────────────────────


class GroupAppointmentRequest(BaseModel):
    barber_id: int
    service_id: int
    data_inicio: datetime
    client_ids: list[int] = Field(min_length=1)


class GroupAppointmentResponse(BaseModel):
    group_id: str
    created: list[AppointmentResponse]


# ── Service Packs (F28) ───────────────────────────────────────────────────────


class ServicePackCreate(BaseModel):
    nome: str
    service_id: int
    n_sessoes: int = Field(ge=1)
    preco: float = Field(ge=0)


class ServicePackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    service_id: int
    tenant_id: int
    n_sessoes: int
    preco: float


class ClientPackCreate(BaseModel):
    client_id: int
    service_pack_id: int
    expira_em: date | None = None


class ClientPackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    service_pack_id: int
    tenant_id: int
    sessoes_restantes: int
    comprado_em: datetime
    expira_em: date | None


# ── Loyalty (F30) ─────────────────────────────────────────────────────────────


class LoyaltyAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    tenant_id: int
    pontos_total: int
    pontos_disponiveis: int
    updated_at: datetime


class LoyaltyRedeemRequest(BaseModel):
    pontos: int = Field(ge=1)
    descricao: str | None = None


class LoyaltyTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    loyalty_account_id: int
    appointment_id: int | None
    pontos: int
    tipo: str
    criado_em: datetime
    descricao: str | None


# -- Campaigns (F33) ----------------------------------------------------------


class CampaignCreate(BaseModel):
    nome: str
    subject: str
    body_template: str
    segment_filters: str = "{}"  # JSON string with segment filter criteria


class CampaignResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    subject: str
    body_template: str
    segment_filters: str
    status: str
    tenant_id: int
    criado_em: datetime
    enviado_em: datetime | None
    total_sent: int


# -- Payments (F34) -----------------------------------------------------------


class CheckoutRequest(BaseModel):
    appointment_id: int


class CheckoutResponse(BaseModel):
    checkout_url: str


class AppointmentPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payment_status: str


# -- Invoices (F35) -----------------------------------------------------------


class InvoiceCreate(BaseModel):
    appointment_id: int


class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    appointment_id: int
    tenant_id: int
    invoice_number: str
    invoice_url: str | None
    status: str
    criado_em: datetime


# ── Products / Stock (F37) ───────────────────────────────────────────────────


class ProductCreate(BaseModel):
    nome: str
    descricao: str | None = None
    stock_atual: int = 0
    stock_minimo: int = 0
    preco_unitario: float = 0


class ProductUpdate(BaseModel):
    nome: str | None = None
    descricao: str | None = None
    stock_atual: int | None = None
    stock_minimo: int | None = None
    preco_unitario: float | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: str | None
    stock_atual: int
    stock_minimo: int
    preco_unitario: float
    tenant_id: int


class StockAdjustRequest(BaseModel):
    delta: int
    reason: str


class ServiceProductCreate(BaseModel):
    service_id: int
    product_id: int
    quantidade: int = Field(ge=1)


class ServiceProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_id: int
    product_id: int
    quantidade: int
    tenant_id: int


# ── Resources / Rooms (F38) ─────────────────────────────────────────────────


class ResourceCreate(BaseModel):
    nome: str
    tipo: str


class ResourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    tipo: str
    tenant_id: int


# ── Clinical Records (F41) ──────────────────────────────────────────────────


class ClinicalRecordUpsert(BaseModel):
    alergias: str | None = None
    notas_saude: str | None = None


class ClinicalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    tenant_id: int
    alergias: str | None
    notas_saude: str | None
    consentimento_assinado: bool
    consentimento_data: datetime | None


class ClinicalNoteCreate(BaseModel):
    nota: str


class ClinicalNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    clinical_record_id: int
    tenant_id: int
    nota: str
    criado_em: datetime
    barber_id: int | None
