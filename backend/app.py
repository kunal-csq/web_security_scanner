import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from api.scan_routes import scan_bp

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = Flask(__name__)
CORS(app)

# Register API blueprint
app.register_blueprint(scan_bp)


@app.route("/")
def home():
    return "WebGuard DAST Engine v2.0 Running"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
