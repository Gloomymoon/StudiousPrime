from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, login_required
from . import main
from models import User


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return redirect(url_for('englicise.index'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    user = User.query.filter_by(name='David').first()
    if user:
        login_user(user, True)
        return redirect(request.args.get('next') or url_for('main.index'))
    flash('Invalid username or password.')
    abort(403)
