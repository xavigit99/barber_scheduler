from pydantic import BaseModel

class ClienteCreate(BaseModel):
    nome: str
    email: str
    telefone: str | None = None

class ClienteResponse(BaseModel):
    id: int
    nome: str
    email: str
    telefone: str | None

    class Config:
        from_attributes = True