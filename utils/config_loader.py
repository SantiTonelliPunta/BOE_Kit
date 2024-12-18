import json
import os
from dotenv import load_dotenv

class ConfigLoader:
    @staticmethod
    def load_config():
        with open('config/config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def load_secrets():
        load_dotenv('config/secrets.env')
        return {
            'smtp_server': os.getenv('SMTP_SERVER'),
            'smtp_port': os.getenv('SMTP_PORT'),
            'sender_email': os.getenv('SENDER_EMAIL'),
            'sender_password': os.getenv('SENDER_PASSWORD'),
            'recipient_email': os.getenv('RECIPIENT_EMAIL')
        } 