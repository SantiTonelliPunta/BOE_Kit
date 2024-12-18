import smtplib
from email.message import EmailMessage

class EmailSender:
    def __init__(self, email_config):
        self.config = email_config

    def send_email(self, subject, content):
        print(f"Enviando email con asunto: {subject}")
        msg = EmailMessage()
        msg.set_content(content)
        msg['Subject'] = subject
        msg['From'] = self.config['sender_email']
        msg['To'] = self.config['recipient_email']

        try:
            with smtplib.SMTP(self.config['smtp_server'], 
                            int(self.config['smtp_port'])) as server:
                server.starttls()
                server.login(self.config['sender_email'], 
                           self.config['sender_password'])
                server.send_message(msg)
                print("Email enviado exitosamente")
        except Exception as e:
            print(f"Error al enviar email: {str(e)}") 