import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_email(
    email_to: str,
    subject: str,
    html_content: str,
) -> None:
    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    message["To"] = email_to

    message.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_TLS:
            server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(message)

def send_verification_email(email_to: str, token: str) -> None:
    verification_url = f"http://localhost:3000/verify-email?token={token}"
    html_content = f"""
    <html>
        <body>
            <h1>Подтверждение email</h1>
            <p>Для подтверждения вашего email, пожалуйста, перейдите по ссылке:</p>
            <p><a href="{verification_url}">Подтвердить email</a></p>
        </body>
    </html>
    """
    send_email(
        email_to=email_to,
        subject="Подтверждение email",
        html_content=html_content,
    ) 