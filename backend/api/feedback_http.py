from backend.application.commands.create_feedback_command import CreateFeedbackCommand
from backend.application.queries.list_admin_feedback_query import ListAdminFeedbackQuery
from backend.application.queries.list_barber_feedback_query import ListBarberFeedbackQuery
from backend.application.queries.list_my_feedback_query import ListMyFeedbackQuery
from backend.infrastructure.schemas import FeedbackCreate


def build_create_feedback_command(
    payload: FeedbackCreate,
    user_id: int,
    tenant_id: int | None = None,
) -> CreateFeedbackCommand:
    return CreateFeedbackCommand(
        appointment_id=payload.appointment_id,
        rating=payload.rating,
        comentario=payload.comentario,
        user_id=user_id,
        tenant_id=tenant_id,
    )


def build_list_barber_feedback_query(
    barber_id: int,
    tenant_id: int | None = None,
) -> ListBarberFeedbackQuery:
    return ListBarberFeedbackQuery(barber_id=barber_id, tenant_id=tenant_id)


def build_list_my_feedback_query(
    user_id: int,
    tenant_id: int | None = None,
) -> ListMyFeedbackQuery:
    return ListMyFeedbackQuery(user_id=user_id, tenant_id=tenant_id)


def build_list_admin_feedback_query(
    tenant_id: int | None = None,
) -> ListAdminFeedbackQuery:
    return ListAdminFeedbackQuery(tenant_id=tenant_id)
