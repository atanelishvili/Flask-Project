from flask import Blueprint
properties_bp = Blueprint('properties', __name__)
from . import routes