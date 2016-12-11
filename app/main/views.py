from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, login_required, logout_user
from . import main
from models import User
from forms import LoginForm


@main.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('english.index'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    user = User.query.filter_by(name='David').first()
    login_user(user, form.remember_me.data)
    return redirect(request.args.get('next') or url_for('main.index'))
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('main/login.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)