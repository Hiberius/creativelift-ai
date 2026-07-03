"""Human login: register, login, session cookie, logout, RBAC enforcement."""

from uuid import UUID

import pytest

from app.core.security import SESSION_COOKIE_NAME
from app.services.core_repositories import core_repository


@pytest.fixture(autouse=True)
def _reset_auth_state():
    store = core_repository.store  # type: ignore[attr-defined]
    store.users_by_email.clear()
    store.users_by_id.clear()
    store.memberships.clear()
    store.user_sessions.clear()
    yield


def _register(client, email=None, org="Lift Co"):
    from uuid import uuid4

    email = email or f"founder-{uuid4().hex[:8]}@example.com"
    return client.post(
        "/v1/auth/register",
        json={
            "email": email,
            "name": "Founder",
            "password": "super-secret-1",
            "organization_name": org,
        },
    )


def test_register_creates_org_owner_and_session_cookie(client):
    response = _register(client, email="founder@example.com")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["user"]["email"] == "founder@example.com"
    assert body["role"] == "owner"
    assert body["organization"]["name"] == "Lift Co"
    assert SESSION_COOKIE_NAME in response.cookies

    session = client.get("/v1/auth/session")
    assert session.status_code == 200
    assert session.json()["user"]["email"] == "founder@example.com"

    me = client.get("/v1/me")
    assert me.status_code == 200
    principal = me.json()["principal"]
    assert principal["role"] == "owner"
    assert principal["organization_id"] == body["organization"]["id"]


def test_duplicate_email_is_rejected(client):
    assert _register(client, email="dup@example.com").status_code == 200
    duplicate = _register(client, email="dup@example.com", org="Another Co")
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "email_taken"


def test_login_with_wrong_password_fails_generic(client):
    _register(client, email="wrongpw@example.com")
    client.cookies.clear()
    bad = client.post(
        "/v1/auth/login",
        json={"email": "wrongpw@example.com", "password": "wrong-password"},
    )
    assert bad.status_code == 401
    assert bad.json()["error"]["code"] == "invalid_credentials"


def test_login_restores_access_and_logout_revokes(client):
    registered = _register(client, email="relogin@example.com")
    organization_id = registered.json()["organization"]["id"]
    client.cookies.clear()

    login = client.post(
        "/v1/auth/login",
        json={"email": "relogin@example.com", "password": "super-secret-1"},
    )
    assert login.status_code == 200, login.text
    assert login.json()["organization"]["id"] == organization_id

    assert client.get("/v1/auth/session").status_code == 200

    logout = client.post("/v1/auth/logout")
    assert logout.status_code == 200
    # The cookie was revoked server-side: even replaying it must fail.
    assert client.get("/v1/auth/session").status_code == 401


def test_session_scopes_data_to_the_users_organization(client):
    registered = _register(client)
    organization_id = registered.json()["organization"]["id"]

    created = client.post(
        "/v1/briefs",
        json={
            "name": "Session brief",
            "objective": "conversion",
            "target_audience": "founders",
            "channel": "email",
            "primary_kpi": "signup",
        },
    )
    assert created.status_code == 200, created.text
    assert created.json()["organization_id"] == organization_id


def test_viewer_cannot_approve_or_manage_api_keys(client):
    registered = _register(client)
    organization_id = UUID(registered.json()["organization"]["id"])
    user_id = UUID(registered.json()["user"]["id"])

    # Demote the user to viewer directly at the repository boundary.
    core_repository.store.memberships.clear()  # type: ignore[attr-defined]
    core_repository.create_membership(user_id, organization_id, "viewer")

    creative = client.post(
        "/v1/creative-treatments",
        json={
            "name": "Viewer target",
            "objective": "conversion",
            "target_audience": "founders",
            "channel": "email",
        },
    )
    assert creative.status_code == 200
    creative_id = creative.json()["id"]

    approve = client.post(
        f"/v1/creative-treatments/{creative_id}/approve", json={"notes": "nope"}
    )
    assert approve.status_code == 403

    key = client.post("/v1/api-keys", json={"name": "viewer-key"})
    assert key.status_code == 403


def test_marketer_can_approve_but_not_manage_api_keys(client):
    registered = _register(client)
    organization_id = UUID(registered.json()["organization"]["id"])
    user_id = UUID(registered.json()["user"]["id"])
    core_repository.store.memberships.clear()  # type: ignore[attr-defined]
    core_repository.create_membership(user_id, organization_id, "marketer")

    creative = client.post(
        "/v1/creative-treatments",
        json={
            "name": "Marketer target",
            "objective": "conversion",
            "target_audience": "founders",
            "channel": "email",
        },
    )
    creative_id = creative.json()["id"]

    approve = client.post(
        f"/v1/creative-treatments/{creative_id}/approve", json={"notes": "ok"}
    )
    assert approve.status_code == 200, approve.text

    key = client.post("/v1/api-keys", json={"name": "marketer-key"})
    assert key.status_code == 403


def test_service_api_key_cannot_approve_creatives(client):
    key = client.post("/v1/api-keys", json={"name": "svc"}).json()
    creative = client.post(
        "/v1/creative-treatments",
        json={
            "name": "Service target",
            "objective": "conversion",
            "target_audience": "founders",
            "channel": "email",
        },
    ).json()

    approve = client.post(
        f"/v1/creative-treatments/{creative['id']}/approve",
        headers={"Authorization": f"Bearer {key['raw_key']}"},
        json={"notes": "bot"},
    )
    assert approve.status_code == 403
