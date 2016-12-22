from flask import Blueprint, current_app

main = Blueprint('main', __name__)

from . import views, errors
from .models import Permission


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.app_context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)


@main.app_context_processor
def inject_str():
    return dict(str=str)


@main.app_context_processor
def inject_len():
    return dict(len=len)


@main.app_context_processor
def inject_len():
    return dict(current_app=current_app)
