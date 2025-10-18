import smtplib
from ..config import config
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .core import get_mail_server


def send_email(receiver: str, subject: str, body: str, html_body: str = None):
    try:
        sender = config.MAIL_ADDRESS
        message = MIMEMultipart("alternative")
        message["From"] = f"System <{sender}>"
        message["To"] = receiver
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain", "utf-8"))

        if html_body:
            html_content = f"""
            <html>
              <body>
                {html_body}
                <br><br>
                <p><i>This is an automated message, do not reply</i></p>
              </body>
            </html>
            """
            message.attach(MIMEText(html_content, "html", "utf-8"))

        server = get_mail_server()
        if not server:
            return {"success": False, "msg": "Mail server connection failed"}

        try:
            server.sendmail(sender, receiver, message.as_string())
        finally:
            server.quit()

        return {"success": True, "msg": "Email sent successfully"}

    except Exception as err:
        return {"success": False, "msg": f"Failed to send email: {err}"}
