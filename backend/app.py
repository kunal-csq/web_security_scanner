import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from api.scan_routes import scan_bp
from api.auth_routes import auth_bp
from api.history_routes import history_bp
from db import init_db

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = Flask(__name__)
CORS(app)

# Initialize database
init_db()

# Register API blueprints
app.register_blueprint(scan_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(history_bp)


@app.route("/")
def home():
    return "WebGuard DAST Engine v2.2 Running"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
