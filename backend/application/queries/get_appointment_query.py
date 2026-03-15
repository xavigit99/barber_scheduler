from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class GetAppointmentQuery(Request):
    appointment_id: int
