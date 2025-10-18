from flask import jsonify
import datetime
from zoneinfo import ZoneInfo
from .config import config
from flask_cors import CORS
from .services.system import get_service_information
from .services.core import get_flask_app
from .services.system import system_check

app = get_flask_app()
app.config["SECRET_KEY"] = config.FLASK_SECRET_KEY
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
app.config["JWT_TOKEN_LOCATION"] = ["headers","cookies"]
app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_COOKIE_SAMESITE"] = "None"
app.config["JWT_COOKIE_HTTPONLY"] = True
app.config["JWT_COOKIE_CSRF_PROTECT"] = True
app.url_map.strict_slashes = False

# ENDPOINTS FROM BLUEPRINTS
from .routes.email import email_bp
app.register_blueprint(email_bp, url_prefix="/")

ph_time = datetime.datetime.now(ZoneInfo("Asia/Manila"))

# status endpoint
@app.route("/", methods=["GET"])
def status():
    data = {
        "msg": "email services is up",
        "date": str(ph_time),
        "info": get_service_information()
    }
    return jsonify(data)

# setup CORS for all endpoint
CORS(app, origins=config.WEB_CLIENT_HOSTS, supports_credentials=True)


# main method
def jarvis_deploy_website():
    system_check()
    
    return app