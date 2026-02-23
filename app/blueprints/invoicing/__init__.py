from flask import Blueprint

invoicing_bp = Blueprint('invoicing', __name__)

from . import routes
