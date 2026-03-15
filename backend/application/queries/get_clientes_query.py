from dataclasses import dataclass
from diator.requests import Request

@dataclass(frozen=True)
class GetClientesQuery(Request):
    pass