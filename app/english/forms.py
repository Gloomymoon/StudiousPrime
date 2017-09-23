from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField, HiddenField, BooleanField, RadioField
from wtforms.validators import Required
from wtforms import ValidationError
from wtforms_components import read_only
from .models import EnglishWord, EnglishBook, EnglishLesson


class NewBookForm(FlaskForm):
    name = StringField('Book Name', validators=[Required()])
    description = TextAreaField('Description')
    cover = StringField('Cover Picture')
    submit = SubmitField('Create')

    def __int__(self, *args, **kwargs):
        super(NewBookForm, self).__init__(*args, **kwargs)

    def validate_name(self, field):
        if EnglishBook.query.filter_by(title=field.data).first():
            raise ValidationError('Title [' + field.data + '] has already been used.')


class EditBookForm(FlaskForm):
    id = HiddenField()
    name = StringField('Book Name')
    description = TextAreaField('Description')
    cover = StringField('Cover Picture')
    submit = SubmitField('Save')

    def __int__(self, *args, **kwargs):
        super(EditBookForm, self).__init__(*args, **kwargs)
        #read_only(self.name)
        
    def validate_name(self, field):
        if EnglishBook.query.filter(EnglishBook.title == field.data, EnglishBook.id != self.id.data).first():
            raise ValidationError('Title [' + field.data + '] has already been used.')


class NewLessonForm(FlaskForm):
    book_id = HiddenField()
    number = StringField('#')
    title = StringField('Lesson', validators=[Required()])
    submit = SubmitField('Create')

    def __init__(self, *args, **kwargs):
        super(NewLessonForm, self).__init__(*args, **kwargs)
        read_only(self.number)


class NewWordForm(FlaskForm):
    book_id = HiddenField()
    book_title = StringField('Book')
    lesson_title = SelectField('Lesson', coerce=int, validators=[Required()])
    english = StringField('English', validators=[Required()])
    chinese = StringField('Chinese', validators=[Required()])
    example = TextAreaField('Example')
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(NewWordForm, self).__init__(*args, **kwargs)
        read_only(self.book_title)
        self.lesson_title.choices = []
        #self.books.choices = [(book.id, book.name) for book in EnglishBook.query.order_by(EnglishBook.id).all()]

    def init_lesson(self, book_id):
        book = EnglishBook.query.filter_by(id=book_id).first_or_404()
        if book:
            self.lesson_title.choices = [(lesson.id, lesson.title) for lesson in book.lessons]

    def validate_english(self, field):
        b = EnglishBook.query.filter_by(id=self.book_id.data).one_or_none()
        w = [word for word in b.get_words() if word.english == field.data]
        if len(w) >= 1:
            raise ValidationError('[' + field.data + '] already existed in this book.')


class EditWordForm(FlaskForm):
    #books = SelectField('Books', coerce=int)
    id = HiddenField()
    book_id = HiddenField()
    book_title = StringField('Book')
    lesson_title = SelectField('Lesson', coerce=int)
    english = StringField('English', validators=[Required()])
    chinese = StringField('Chinese', validators=[Required()])
    example = TextAreaField('Example')
    submit = SubmitField('Update')

    def __init__(self, *args, **kwargs):
        super(EditWordForm, self).__init__(*args, **kwargs)
        read_only(self.book_title)
        self.lesson_title.choices = []
        #self.books.choices = [(book.id, book.name) for book in EnglishBook.query.order_by(EnglishBook.id).all()]

    def init_lesson(self, book_id):
        book = EnglishBook.query.filter_by(id=book_id).first_or_404()
        if book:
            self.lesson_title.choices = [(lesson.id, lesson.title) for lesson in book.lessons]

    def validate_english(self, field):
        b = EnglishBook.query.filter_by(id=self.book_id.data).one_or_none()
        w = [word for word in b.get_words() if word.english == field.data and word.id != self.id.data]
        if len(w) >= 1:
            raise ValidationError('[' + field.data + '] already existed in this book.')


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


