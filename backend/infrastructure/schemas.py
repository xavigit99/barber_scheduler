from pydantic import BaseModel


class ClientBase(BaseModel):
    nome: str
    email: str
    telefone: str | None = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    telefone: str | None = None


class ClientResponse(ClientBase):
    id: int

    class Config:
        from_attributes = True


ClienteCreate = ClientCreate
ClienteUpdate = ClientUpdate
ClienteResponse = ClientResponse
