import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """
    Service responsável pelo envio de comunicações via Email.
    """
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_pass = settings.SMTP_PASSWORD

    def send_alert(self, recipient: str, subject: str, body: str) -> bool:
        """
        Envia um email de alerta de forma síncrona.
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = recipient
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            # Simulação de envio (em prod usaríamos smtplib real ou provider)
            logger.info(f"Simulando envio de email para {recipient}: {subject}")
            
            # Em um ambiente real:
            # with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            #     server.starttls()
            #     server.login(self.smtp_user, self.smtp_pass)
            #     server.send_message(msg)
            
            return True
        except Exception as e:
            logger.error(f"Falha ao enviar email: {str(e)}")
            return False
