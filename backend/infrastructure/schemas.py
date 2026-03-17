from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from backend.core.roles import ADMIN_ROLE, BARBER_ROLE, CLIENT_ROLE


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


class AppointmentCreateRequest(BaseModel):
    barber_id: int
    client_id: int
    service_id: int
    data_inicio: datetime


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


class ClientBase(BaseModel):
    nome: str
    email: str
    telefone: str | None = None


class ClientCreate(ClientBase):
    tenant_id: int


class ClientUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None
    tenant_id: int | None = None


class ClientResponse(ClientBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True


class ServiceBase(BaseModel):
    nome: str
    duracao_minutos: int = Field(gt=0)
    preco: float = Field(ge=0)


class ServiceCreate(ServiceBase):
    tenant_id: int


class ServiceUpdate(BaseModel):
    nome: str | None = None
    duracao_minutos: int | None = Field(default=None, gt=0)
    preco: float | None = Field(default=None, ge=0)
    tenant_id: int | None = None


class ServiceResponse(ServiceBase):
    id: int
    tenant_id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: str
    role: Literal[ADMIN_ROLE, BARBER_ROLE, CLIENT_ROLE]


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
    tenant_id: int


class BootstrapAdminRequest(BaseModel):
    username: str
    email: str
    password: str = Field(min_length=8)


class AuthLoginRequest(BaseModel):
    username: str
    password: str = Field(min_length=8)


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
