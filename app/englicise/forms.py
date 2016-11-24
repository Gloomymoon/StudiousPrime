from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, SelectMultipleField, IntegerField
from wtforms.validators import Required
from wtforms import ValidationError
from wtforms_components import read_only
from .models import EnglishWord, EnglishBook


class NewWordForm(FlaskForm):
    english = StringField('English', validators=[Required()])
    chinese = StringField('Chinese', validators=[Required()])
    example = TextAreaField('Example')
    #books = SelectMultipleField('Books', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(NewWordForm, self).__init__(*args, **kwargs)
        #self.books.choices = [(book.id, book.name) for book in EnglishBook.query.order_by(EnglishBook.id).all()]


class EditWordForm(FlaskForm):
    #books = SelectField('Books', coerce=int)
    english = StringField('English', validators=[Required()])
    chinese = StringField('Chinese', validators=[Required()])
    example = TextAreaField('Example')
    submit = SubmitField('Update')

    def __init__(self, *args, **kwargs):
        super(EditWordForm, self).__init__(*args, **kwargs)
        #read_only(self.books)
        #self.books.choices = [(book.id, book.name) for book in EnglishBook.query.order_by(EnglishBook.id).all()]

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


class LevelSettingForm(FlaskForm):
    total = IntegerField('Total', render_kw={"data-min": "1"})
    level1 = IntegerField('Level 1', render_kw={"data-min": "0"})
    level2 = IntegerField('2', render_kw={"data-min": "0"})
    level3 = IntegerField('3', render_kw={"data-min": "0"})
    level4 = IntegerField('4', render_kw={"data-min": "0"})
    level5 = IntegerField('5', render_kw={"data-min": "0"})
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(LevelSettingForm, self).__init__(*args, **kwargs)
        read_only(self.total)
        read_only(self.level1)
        read_only(self.level2)
        read_only(self.level3)
        read_only(self.level4)
        read_only(self.level5)
