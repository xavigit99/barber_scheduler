from dataclasses import dataclass

from diator.requests import Request


@dataclass(frozen=True)
class CancelAppointmentCommand(Request):
    appointment_id: int
