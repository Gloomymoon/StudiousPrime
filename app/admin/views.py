from flask import request, render_template, current_app, flash
from flask_login import login_required
from ..main.models import User, Permission, Role
from ..main.decorators import permission_required
from . import admin
from app import db
from forms import EditUserAdminForm


@admin.route('/users/')
@login_required
@permission_required(Permission.ADMINISTER)
def users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id).paginate(
        page, per_page=current_app.config['USERS_PER_PAGE'],
        error_out=False)
    users = pagination.items
    return render_template('admin/users.html', users=users, pagination=pagination)


@admin.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.ADMINISTER)
def edit_user(id):
    user = User.query.get_or_404(id)
    form = EditUserAdminForm()
    if form.validate_on_submit():
        user.email = form.email.data
        if form.password.data:
            user.password = form.password.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        db.session.add(user)
        db.session.commit()
        flash("User profile updated.")
    form.username.data = user.name
    form.email.data = user.email
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id

    return render_template('admin/user.html', user=user, form=form)
