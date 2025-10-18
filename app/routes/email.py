from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from ..services.email import send_email
from ..services.validation import check_json_payload
from threading import Event
import time

email_bp = Blueprint("email", __name__)


@email_bp.route("/send", methods=["POST"])
@jwt_required()
def send_bulk_email():
    try:
        # validate payload
        data, error_response = check_json_payload()
        if error_response:
            return error_response
        sender_name = data.get("sender_name")
        sender_email = data.get("sender_email")
        receivers = data.get("receivers")
        subject = data.get("header")
        body = data.get("body")
        html_body = data.get("html_body")

        # checkers
        if not all([sender_name, sender_email, receivers, subject, body]):
            return jsonify({"success": False, "msg": "Missing required parameters"}), 400

        if not isinstance(receivers, list) or not receivers:
            return jsonify({"success": False, "msg": "Receivers must be a non-empty list"}), 400

        # setup email send
        results = []
        delay_seconds = 1
        stop_event = Event()

        for index, recipient in enumerate(receivers, start=1):
            if stop_event.is_set():
                break

            composed_body = f"{body}\n\nSent by: {sender_name} <{sender_email}>"

            # compose html body
            composed_html = None
            if html_body:
                composed_html = f"""
                <html>
                  <body style="font-family: Arial, sans-serif;">
                    {html_body}
                    <br><br>
                    <p style="font-size: 0.9em; color: gray;">
                      Sent by: <b>{sender_name}</b> &lt;{sender_email}&gt;
                    </p>
                    <br><br>
                    <p style="font-size: 0.9em; color: gray;">
                      This is an automated message, do not reply
                    </p>
                  </body>
                </html>
                """

            # send email
            result = send_email(
                receiver=recipient,
                subject=subject,
                body=composed_body,
                html_body=composed_html
            )

            results.append({
                "recipient": recipient,
                "status": "success" if result["success"] else "failed",
                "message": result["msg"]
            })

            # timeout
            if index < len(receivers):
                time.sleep(delay_seconds)

        all_success = all(r["status"] == "success" for r in results)

        return jsonify({
            "success": all_success,
            "summary": {
                "sent": sum(1 for r in results if r["status"] == "success"),
                "failed": sum(1 for r in results if r["status"] == "failed"),
                "total": len(results)
            },
            "results": results
        }), 200 if all_success else 207  # 207 = partial

    except Exception as err:
        return jsonify({
            "success": False,
            "msg": f"Failed to send bulk email: {err}"
        }), 500
