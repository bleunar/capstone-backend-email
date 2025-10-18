import json, os

def get_service_information():
    base = os.path.dirname(__file__)
    path = os.path.join(base, "..", "service_information.json")
    with open(path, 'r') as f:
        return json.load(f)


# system startup check
def system_check() -> bool:
    from .core import  get_mail_server
    from .log import log

    log.inform("SYSTEM-CHECK", f"\n{'/'*25}  System Check  {25*'/'}\n")
    log.inform("SYSTEM-CHECK", "Starting system check...")

    # MAIL SERVER
    if get_mail_server():
        log.inform("SYSTEM-CHECK", "Mail server connection established")
    else:
        log.error("SYSTEM-CHECK", "Failed to connect to mail server")
        return False
    

    log.inform("SYSTEM-CHECK", "critical checks completed")
    log.inform("SYSTEM-CHECK", f"\n{'\\'*25}  System Check End  {25*'\\'}\n")