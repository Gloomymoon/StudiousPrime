from flask import Blueprint

english = Blueprint('english', __name__)

from . import views

