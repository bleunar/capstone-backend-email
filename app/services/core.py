from ..config import config
import json
import smtplib
import time
from flask_jwt_extended import JWTManager
from flask import Flask
from .log import log
from prometheus_flask_exporter import PrometheusMetrics

# instance of flask and jwt
app = Flask(__name__)
jwt = JWTManager(app)


# instance fetch
def get_flask_app():
    metrics = PrometheusMetrics(app)
    return app

def get_jwt_manager():
    return jwt


def get_mail_server():
    try:
        port = int(config.MAIL_SERVER_PORT)
        host = config.MAIL_SERVER_ADDRESS

        # Use SSL if port 465, otherwise STARTTLS
        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=10)
        else:
            server = smtplib.SMTP(host, port, timeout=10)
            server.ehlo()
            server.starttls()
            server.ehlo()

        server.login(config.MAIL_ADDRESS, config.MAIL_PASSKEY)
        return server

    except smtplib.SMTPException as e:
        log.error("MAIL_SRV-ERR", f"SMTP error: {e}")
        return None
    except Exception as e:
        log.error("MAIL_SRV-ERR", f"Failed to connect with mail server: {e}")
        return None