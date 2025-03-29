from core.config import settings

class MailService:
    def __init__(self):
        self.SMTP_HOST = settings.SMTP_HOST
        self.SMTP_PORT = settings.SMTP_PORT
        self.SMTP_USER = settings.SMTP_USER
        self.SMTP_PASSWORD = settings.SMTP_PASSWORD

    async def create_registration():
        pass