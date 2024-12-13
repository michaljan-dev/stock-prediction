from app import app
from flask import Blueprint

# Define the blueprint:
sinet_market = Blueprint("sinet_market", __name__, url_prefix="/sinet/stock")
app.register_blueprint(sinet_market)
