from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import Required
from wtforms import ValidationError
from wtforms_components import read_only
from .models import EnglishWord, EnglishBook


class NewWordForm(FlaskForm):
    book = SelectField('Book', coerce=int)
    english = StringField('English', validators=[Required()])
    chinese = StringField('Chinese', validators=[Required()])
    example = TextAreaField('Example')
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(NewWordForm, self).__init__(*args, **kwargs)
        self.book.choices = [(book.id, book.name) for book in EnglishBook.query.order_by(EnglishBook.id).all()]

    def validate_english(self, field):
        if EnglishWord.query.filter_by(english=field.data).first():
            raise ValidationError('English word [' + field.data + '] already added.')


class EditWordForm(FlaskForm):
    book = SelectField('Book', coerce=int)
    english = StringField('English', validators=[Required()])
    chinese = StringField('Chinese', validators=[Required()])
    example = TextAreaField('Example')
    submit = SubmitField('Update')

    def __init__(self, *args, **kwargs):
        super(EditWordForm, self).__init__(*args, **kwargs)
        read_only(self.book)
        self.book.choices = [(book.id, book.name) for book in EnglishBook.query.order_by(EnglishBook.id).all()]

    def validate_english(self, field):
        w = EnglishWord.query.filter_by(english=field.data).all()
        if len(w) > 1:
            raise ValidationError('English word [' + field.data + '] already existed.')


class QuestionForm(FlaskForm):
    word_mask = StringField('', validators=[Required()])
    submit = SubmitField('Next')

    def validate_word_mask(self, field):
        if '_' in field.data:
            field.data = ''
            raise ValidationError('Please fill in all the blanks.')
