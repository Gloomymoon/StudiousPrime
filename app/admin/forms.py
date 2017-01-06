from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import Required, Length, Regexp, EqualTo, Email
from wtforms import ValidationError
from app.main.models import User, Role


class EditUserAdminForm(FlaskForm):
    username = StringField('Name')
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    password = StringField('Password (leave blank if no change made)')
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Update')

    def __init__(self, *args, **kwargs):
        super(EditUserAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]