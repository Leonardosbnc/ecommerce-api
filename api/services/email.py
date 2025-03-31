from postmarker.core import PostmarkClient
from api.config import settings


class EmailService:
    def __init__(self):
        self.client = PostmarkClient(server_token=settings.email.token)
        self.from_email = settings.email.default_from

    def send_email_confirmation(self, token: str, email: str):
        self.client.emails.send(
            From=self.from_email,
            To=email,
            Subject="Confirm your account",
            HtmlBody=f"<html><body><strong>Hello!</strong><p>Use this token: <strong>{token}</strong> to confirm your account.</p></body></html>",
        )

    def send_reset_password_email(self, token: str, email: str):
        self.client.emails.send(
            From=self.from_email,
            To=email,
            Subject="Reset your Password",
            HtmlBody=f"<html><body><strong>Hello!</strong><p>Use this token: <strong>{token}</strong> to recover your password.</p></body></html>",
        )
