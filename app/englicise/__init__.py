from flask import Blueprint

englicise = Blueprint('englicise', __name__)

from . import views

