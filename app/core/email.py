from typing import Any, Dict
from pathlib import Path
from jinja2 import Environment, select_autoescape, PackageLoader
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from email_validator import validate_email
from pydantic import EmailStr, BaseModel
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailSchema(BaseModel):
    email: EmailStr

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=settings.SMTP_TLS,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "email-templates"
)

async def send_email(
    email_to: str,
    subject_template: str,
    html_template_name: str,
    environment: Dict[str, Any],
) -> None:
    logger.info(f"Attempting to send email to {email_to}")

    if not settings.EMAILS_ENABLED:
        logger.warning("Email sending is disabled in settings")
        return

    try:
        validated_email = validate_email(email_to)
        email_to = validated_email.normalized

        env = Environment(
            loader=PackageLoader("app", "email-templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )
        template = env.get_template(html_template_name)
        html_content = template.render(**environment)
        logger.info("Email template rendered successfully")

        message = MessageSchema(
            subject=subject_template,
            recipients=[email_to],
            body=html_content,
            subtype="html"
        )

        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info(f"Email sent successfully to {email_to}")
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}", exc_info=True)
        raise

async def send_verification_email(
    email_to: str,
    token: str,
) -> None:
    logger.info(f"Preparing verification email for {email_to}")
    try:
        await send_email(
            email_to=email_to,
            subject_template="Подтверждение регистрации",
            html_template_name="verification.html",
            environment={
                "verification_url": f"{settings.SERVER_HOST}/verify?token={token}"
            },
        )
        logger.info(f"Verification email sent successfully to {email_to}")
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}", exc_info=True)
        raise

async def send_password_set_email(
    email_to: str,
    token: str,
) -> None:
    logger.info(f"Preparing password set email for {email_to}")
    try:
        await send_email(
            email_to=email_to,
            subject_template="Установка пароля",
            html_template_name="password_set.html",
            environment={
                "password_set_url": f"{settings.SERVER_HOST}/set-password?token={token}"
            },
        )
        logger.info(f"Password set email sent successfully to {email_to}")
    except Exception as e:
        logger.error(f"Failed to send password set email: {str(e)}", exc_info=True)
        raise
