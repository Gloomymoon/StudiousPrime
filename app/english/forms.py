from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField, HiddenField, BooleanField, RadioField
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
    answer = StringField('', validators=[Required()])
    submit = SubmitField('Next')
    word_mask = HiddenField()

    def validate_answer(self, field):
        if '_' in field.data:
            field.data = ''
            raise ValidationError('Please fill in all the blanks.')


class LevelSettingForm(FlaskForm):
    total = IntegerField('Total Questions', render_kw={"data-min": "1", "data-max": "100"})
    level1 = IntegerField('Level 1', render_kw={"data-min": "0"})
    level2 = IntegerField('2', render_kw={"data-min": "0"})
    level3 = IntegerField('3', render_kw={"data-min": "0"})
    level4 = IntegerField('4', render_kw={"data-min": "0"})
    level5 = IntegerField('5', render_kw={"data-min": "0"})
    fill_down = BooleanField('Fill Down')
    fill_level5 = BooleanField('Fill level 5')
    use_mask = BooleanField('Use Mask')
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(LevelSettingForm, self).__init__(*args, **kwargs)
        read_only(self.total)
        read_only(self.level1)
        read_only(self.level2)
        read_only(self.level3)
        read_only(self.level4)
        read_only(self.level5)


class RecognitionForm(FlaskForm):
    total = IntegerField('Total Questions', render_kw={"data-min": "1", "data-max": "100"})
    timeout = IntegerField('Timeout', render_kw={"data-min": "0", "data-max": "60"})
    english_question = RadioField('Question is', choices=[(0, 'Chinese'), (1, 'English')], coerce=int)
    use_image = RadioField('Chinese as', choices=[(0, 'Text   '), (1, 'Image')], coerce=int)

    submit = SubmitField('Start New')


