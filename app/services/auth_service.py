"""Authentication business logic for marketing team members."""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.clients.klaviyo_client import KlaviyoClient, KlaviyoClientError
from app.core.config import Settings
from app.core.logging import logger
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.exceptions.http_exceptions import ForbiddenError, UnauthorizedError
from app.models.user import MARKETING_TEAM_MEMBER_ROLE
from app.repositories.password_reset_token_repository import (
    PasswordResetTokenRepository,
)
from app.repositories.user_repository import UserRepository
from app.schemas.marketing_team_member import (
    ForgotPasswordData,
    LoginData,
    TokenPair,
    UserSummary,
)

FORGOT_PASSWORD_GENERIC_MESSAGE = (
    "If an account exists for this email, a password reset link has been sent."
)
INVALID_CREDENTIALS_MESSAGE = "Invalid email/username or password."


class AuthService:
    """Handles login and forgot-password flows for marketing team members."""

    def __init__(
        self,
        db: Session,
        settings: Settings,
        klaviyo_client: KlaviyoClient | None = None,
    ) -> None:
        """Initialize with database session and settings."""
        self._db = db
        self._settings = settings
        self._user_repo = UserRepository(db)
        self._reset_repo = PasswordResetTokenRepository(db)
        self._klaviyo = klaviyo_client or KlaviyoClient(settings)

    def login(self, email_or_username: str, password: str) -> LoginData:
        """Authenticate a marketing team member and issue JWT tokens."""
        user = self._user_repo.get_by_email_or_username(email_or_username.strip())

        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedError(
                message=INVALID_CREDENTIALS_MESSAGE,
                code="INVALID_CREDENTIALS",
            )

        if not user.is_active:
            raise ForbiddenError(
                message="Your account is inactive. Contact an administrator.",
                code="ACCOUNT_INACTIVE",
            )

        if user.role != MARKETING_TEAM_MEMBER_ROLE:
            raise ForbiddenError(
                message="You are not authorized to access this application.",
                code="ACCESS_DENIED",
            )

        token_subject = {"sub": str(user.id)}
        access_token = create_access_token(token_subject, self._settings)
        refresh_token = create_refresh_token(token_subject, self._settings)

        return LoginData(
            tokens=TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
            ),
            user=UserSummary.model_validate(user),
        )

    def forgot_password(self, email: str) -> ForgotPasswordData:
        """Initiate password recovery; always returns a generic success message."""
        user = self._user_repo.get_by_email_insensitive(email.strip())

        if user is not None and user.is_active and user.role == MARKETING_TEAM_MEMBER_ROLE:
            raw_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
            expires_at = datetime.now(UTC) + timedelta(
                hours=self._settings.password_reset_token_expire_hours,
            )

            self._reset_repo.invalidate_active_tokens_for_user(user.id)
            self._reset_repo.create_token(user.id, token_hash, expires_at)

            try:
                self._klaviyo.send_password_reset_email(user.email, raw_token)
            except KlaviyoClientError as exc:
                logger.warning(
                    "Klaviyo password reset delivery failed for {}: {}",
                    user.email,
                    exc,
                )

        return ForgotPasswordData(message=FORGOT_PASSWORD_GENERIC_MESSAGE)
