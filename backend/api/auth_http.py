from backend.application.commands.authenticate_user_command import AuthenticateUserCommand
from backend.application.commands.bootstrap_admin_command import BootstrapAdminCommand
from backend.application.commands.create_user_command import CreateUserCommand
from backend.application.queries.get_user_query import GetUserQuery
from backend.infrastructure.schemas import (
    AuthLoginRequest,
    BootstrapAdminRequest,
    ClientRegisterRequest,
    UserCreateRequest,
)


def build_bootstrap_admin_command(payload: BootstrapAdminRequest) -> BootstrapAdminCommand:
    return BootstrapAdminCommand(
        username=payload.username,
        email=payload.email,
        password=payload.password,
    )


def build_authenticate_user_command(payload: AuthLoginRequest) -> AuthenticateUserCommand:
    return AuthenticateUserCommand(
        username=payload.username,
        password=payload.password,
    )


def build_create_user_command(payload: UserCreateRequest) -> CreateUserCommand:
    return CreateUserCommand(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        role=payload.role,
    )


def build_register_client_command(payload: ClientRegisterRequest) -> CreateUserCommand:
    return CreateUserCommand(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        role="client",
    )


def build_get_user_query(user_id: int) -> GetUserQuery:
    return GetUserQuery(user_id=user_id)
