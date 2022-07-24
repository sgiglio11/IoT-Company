import os

class DefaultConfig:
    FLASK_KEY = os.environ.get("FlaskKey", "")
    EMAIL_MANAGER = os.environ.get("EmailKey1", "")
    EMAIL_PROTOTYPE = os.environ.get("EmailKey2", "")
