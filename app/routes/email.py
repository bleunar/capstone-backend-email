from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required
from threading import Event
import time
from ..services.validation import check_json_payload, common_error_response
from ..services.email import send_email

email_bp = Blueprint("email", __name__)


# mapping of actions
ACTION_LABELS = {
    "system_unit_name": "System Unit Name",
    "monitor_name": "Monitor Name",
    "keyboard_name": "Keyboard Name",
    "mouse_name": "Mouse Name",
    "avr_name": "AVR Name",
    "headset_name": "Headset Name",
    "system_unit_serial_number": "System Unit Serial No.",
    "monitor_serial_number": "Monitor Serial No.",
    "keyboard_serial_number": "Keyboard Serial No.",
    "mouse_serial_number": "Mouse Serial No.",
    "avr_serial_number": "AVR Serial No.",
    "headset_serial_number": "Headset Serial No.",
    "requires_avr": "Requires AVR",
    "requires_headset": "Requires Headset",
    "plugged_power_cable": "Power Cable Plugged",
    "plugged_display_cable": "Display Cable Plugged",
    "connectivity": "Connectivity",
    "performance": "Performance",
    "status": "Status",
    "name": "Equipment Name",
    "issue": "Issue Reported"
}


@email_bp.route("/send/activity", methods=["POST"])
@jwt_required()
def send_system_activity_email():
    try:
        # --- Validate payload ---
        data, error_response = check_json_payload()
        if error_response:
            return error_response

        receivers = data.get("accounts", [])
        locations = data.get("locations", [])
        cleared_activities = data.get("cleared_activities", [])

        if not receivers or not locations:
            return jsonify({
                "success": False,
                "msg": "Missing 'accounts' or 'locations' in request payload."
            }), 400

        subject = "SYSTEM UPDATES: CLAIMS"

        # --- Start HTML email body ---
        html_body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background-color: #f9f9f9;
                    color: #333;
                    padding: 20px;
                }}
                h2 {{
                    color: #004085;
                    margin-bottom: 10px;
                }}
                h3 {{
                    color: #0056b3;
                    margin-top: 30px;
                    margin-bottom: 10px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                    margin-bottom: 20px;
                    font-size: 14px;
                }}
                th, td {{
                    padding: 8px 10px;
                    border: 1px solid #ccc;
                    text-align: left;
                    vertical-align: top;
                }}
                th {{
                    background-color: #004085;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                .equip-header {{
                    background-color: #e9ecef;
                    font-weight: bold;
                    color: #004085;
                }}
                .footer {{
                    font-size: 0.9em;
                    color: #666;
                    margin-top: 30px;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <h2>{subject}</h2>
            <p>Below are the latest activity updates recorded across your monitored locations:</p>
        """

        # --- Loop through each location and group activities ---
        for loc in locations:
            location_name = loc.get("location_name", "Unknown Location")
            activities = loc.get("activities", [])

            if not activities:
                continue

            # Group activities by equipment_set_name
            grouped_by_equipment = {}
            for act in activities:
                eq_name = act.get("equipment_set_name", "Unnamed Equipment")
                grouped_by_equipment.setdefault(eq_name, []).append(act)

            # Location section
            html_body += f"""
            <h3>{location_name}</h3>
            <table>
                <thead>
                    <tr>
                        <th>Equipment Set</th>
                        <th>Action</th>
                        <th>Previous Value</th>
                        <th>Current Value</th>
                    </tr>
                </thead>
                <tbody>
            """

            # Add grouped rows
            for eq_name, acts in grouped_by_equipment.items():
                # Equipment header row
                html_body += f"""
                    <tr class="equip-header">
                        <td colspan="4">{eq_name}</td>
                    </tr>
                """

                # List all actions for this equipment
                for act in acts:
                    readable_action = ACTION_LABELS.get(act.get('action', ''), act.get('action', '—'))
                    html_body += f"""
                        <tr>
                            <td></td>
                            <td><b>{readable_action}</b></td>
                            <td>{act.get('previous_value') or '—'}</td>
                            <td>{act.get('current_value') or '—'}</td>
                        </tr>
                    """

            html_body += "</tbody></table>"

        # Footer
        html_body += """
            <div class="footer">
                <p>This is an automated system update email. Please do not reply.</p>
            </div>
        </body>
        </html>
        """

        # --- Send emails to all receivers ---
        results = []
        delay_seconds = 1
        stop_event = Event()

        for index, recipient in enumerate(receivers, start=1):
            if stop_event.is_set():
                break

            result = send_email(
                receiver=recipient,
                subject=subject,
                html_body=html_body
            )

            if isinstance(result, tuple):
                success, message = result
            else:
                success = result.get("success", False)
                message = result.get("msg", "Unknown error")

            results.append({
                "recipient": recipient,
                "status": "success" if success else "failed",
                "message": message
            })

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
            "results": results,
            "cleared_activities": cleared_activities
        }), 200 if all_success else 207

    except Exception as err:
        print("Email sending error:", err)
        return jsonify({
            "success": False,
            "msg": f"Failed to send bulk email: {err}"
        }), 500
