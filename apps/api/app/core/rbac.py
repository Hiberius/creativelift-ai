from collections.abc import Callable
from enum import StrEnum

from app.core.errors import ApiError
from app.core.security import ApiPrincipal


class Role(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Permission(StrEnum):
    READ = "read"
    WRITE = "write"
    APPROVE = "approve"
    ADMIN = "admin"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.OWNER: {Permission.READ, Permission.WRITE, Permission.APPROVE, Permission.ADMIN},
    Role.ADMIN: {Permission.READ, Permission.WRITE, Permission.APPROVE},
    Role.MEMBER: {Permission.READ, Permission.WRITE},
    Role.VIEWER: {Permission.READ},
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS[role]


def require_permission(permission: Permission) -> Callable[[ApiPrincipal], ApiPrincipal]:
    def dependency(principal: ApiPrincipal) -> ApiPrincipal:
        if permission.value not in principal.scopes and "admin:demo" not in principal.scopes:
            raise ApiError(403, "forbidden", "Insufficient permissions")
        return principal

    return dependency
