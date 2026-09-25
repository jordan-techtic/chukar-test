"""Authentication business logic for marketing team members."""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.clients.klaviyo_client import KlaviyoClient, KlaviyoClientError
from app.core.config import Settings
from app.core.logging import logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from app.exceptions.http_exceptions import ForbiddenError, UnauthorizedError
from app.models.password_reset_token import PasswordResetToken
from app.models.user import MARKETING_TEAM_MEMBER_ROLE, User
from app.repositories.password_reset_token_repository import (
    PasswordResetTokenRepository,
)
from app.repositories.user_repository import UserRepository
from app.schemas.marketing_team_member import (
    ForgotPasswordData,
    LoginData,
    UserSummary,
)

FORGOT_PASSWORD_MESSAGE = (
    "If an account exists for this email, a password reset link has been sent."
)
INVALID_CREDENTIALS_MESSAGE = "Invalid email/username or password."


class AuthService:
    """Handles login and password recovery for marketing team members."""

    def __init__(
        self,
        db: Session,
        settings: Settings,
        klaviyo_client: KlaviyoClient | None = None,
    ) -> None:
        """Initialize auth service with database session and settings."""
        self._db = db
        self._settings = settings
        self._user_repo = UserRepository(db)
        self._reset_repo = PasswordResetTokenRepository(db)
        self._klaviyo = klaviyo_client or KlaviyoClient(settings)

    def login(self, email_or_username: str, password: str) -> LoginData:
        """Authenticate a marketing team member and issue JWT tokens.

        Args:
            email_or_username: Registered email or username.
            password: Account password.

        Returns:
            LoginData with access/refresh tokens and user summary.

        Raises:
            UnauthorizedError: Invalid credentials.
            ForbiddenError: User inactive or not authorized.
        """
        user = self._user_repo.get_by_email_or_username(email_or_username)
        if user is None or not verify_password(password, user.password_hash):
            raise UnauthorizedError(
                message=INVALID_CREDENTIALS_MESSAGE,
                code="INVALID_CREDENTIALS",
            )

        self._ensure_authorized_marketing_member(user)

        token_subject = {"sub": str(user.id)}
        access_token = create_access_token(token_subject, self._settings)
        refresh_token = create_refresh_token(token_subject, self._settings)

        logger.info("User {} logged in successfully", user.email)

        return LoginData(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserSummary(
                id=str(user.id),
                email=user.email,
                username=user.username,
                role=user.role,
            ),
        )

    def forgot_password(self, email: str) -> ForgotPasswordData:
        """Initiate password recovery for a registered email.

        Always returns a generic success message to prevent email enumeration.

        Args:
            email: Email address to recover.

        Returns:
            ForgotPasswordData with generic confirmation message.
        """
        user = self._user_repo.get_by_email(email)

        if user is not None:
            try:
                self._ensure_authorized_marketing_member(user)
                self._initiate_password_reset(user)
            except ForbiddenError:
                logger.info(
                    "Password reset requested for inactive/unauthorized user {}",
                    email,
                )
            except KlaviyoClientError as exc:
                logger.error(
                    "Failed to send password reset email for {}: {}",
                    email,
                    exc,
                )
            except Exception as exc:
                logger.exception(
                    "Unexpected error during password reset for {}: {}",
                    email,
                    exc,
                )

        return ForgotPasswordData(message=FORGOT_PASSWORD_MESSAGE)

    def _ensure_authorized_marketing_member(self, user: User) -> None:
        """Verify user is an active marketing team member.

        Raises:
            ForbiddenError: User is inactive or has wrong role.
        """
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

    def _initiate_password_reset(self, user: User) -> None:
        """Create reset token and send email via Klaviyo."""
        raw_token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self._settings.password_reset_token_expire_minutes
        )

        self._reset_repo.invalidate_existing_for_user(user.id)
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self._reset_repo.create(reset_token)

        reset_link = (
            f"{self._settings.frontend_reset_url.rstrip('/')}"
            f"?token={raw_token}&email={user.email}"
        )
        self._klaviyo.send_password_reset_email(
            to_email=user.email,
            reset_link=reset_link,
            user_name=user.username,
        )

    @staticmethod
    def _hash_token(raw_token: str) -> str:
        """Return SHA-256 hash of a raw reset token."""
        return hashlib.sha256(raw_token.encode()).hexdigest()
