from backend.application.commands.create_billing_portal_command import (
    CreateBillingPortalCommand,
)
from backend.application.commands.create_subscription_checkout_command import (
    CreateSubscriptionCheckoutCommand,
)
from backend.infrastructure.schemas import BillingCheckoutRequest


def build_create_subscription_checkout_command(
    barbershop_id: int,
    payload: BillingCheckoutRequest,
    *,
    owner_user_id: int,
) -> CreateSubscriptionCheckoutCommand:
    return CreateSubscriptionCheckoutCommand(
        barbershop_id=barbershop_id,
        plan=payload.plan,
        owner_user_id=owner_user_id,
    )


def build_create_billing_portal_command(
    barbershop_id: int,
    *,
    owner_user_id: int,
) -> CreateBillingPortalCommand:
    return CreateBillingPortalCommand(
        barbershop_id=barbershop_id,
        owner_user_id=owner_user_id,
    )
