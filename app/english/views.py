from datetime import datetime
from flask import render_template, flash, request, current_app, redirect, url_for, abort
from flask_login import login_required, current_user
from sqlalchemy import and_, not_
from . import english
from app import db
from .forms import NewWordForm, EditWordForm, QuestionForm, LevelSettingForm
from .models import EnglishWord, EnglishMyWord, EnglishMyExercise, EnglishBook, \
    EnglishSetting, EnglishMyBook, EnglishLesson


@english.route('/')
@login_required
def index():
    newwords = current_user.random_words(1, 1)
    newword = None
    if newwords:
        newword=newwords[0]
    error_words = current_user.error_words(number=5)
    return render_template('english/index.html', error_words=error_words, newword=newword)


@english.route('/add-word', methods=['GET', 'POST'])
@login_required
def add_word():
    back_href = request.args.get('back', '', type=str)
    if not back_href:
        back_href = url_for('english.words')
    form = NewWordForm()
    if form.validate_on_submit():
        word = EnglishWord.query.filter_by(english=form.english.data).first()
        if not word:
            word = EnglishWord()
            #word.book = EnglishBook.query.get(form.book.data)
            word.english = form.english.data
            word.chinese = form.chinese.data
            word.example = form.example.data
            db.session.add(word)
            db.session.commit()
        ws = EnglishMyWord.query.filter_by(word_id=word.id).filter_by(user_id=current_user.id).first()
        if not ws:
            ws = EnglishMyWord(word_id=word.id, user_id=current_user.id)
            db.session.add(ws)
            db.session.commit()
            flash('New word [' + word.english + '] has been added.')
        else:
            flash('Word [' + word.english + '] already added.')
    return render_template('english/add_word.html', form=form, back_href=back_href)


@english.route('/word/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_word(id):
    back_href = request.args.get('back', '', type=str)
    if not back_href:
        back_href = url_for('english.words')
    form = EditWordForm()
    word = EnglishWord.query.filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        word.english = form.english.data
        word.chinese = form.chinese.data
        word.example = form.example.data
        word.update = datetime.utcnow()
        db.session.add(word)
        db.session.commit()
        flash('Word [' + word.english + '] has been updated.')
        return redirect(back_href)
    form.english.data = word.english
    form.chinese.data = word.chinese
    form.example.data = word.example
    return render_template('english/edit_word.html', form=form, back_href=back_href)


@english.route('/words')
@login_required
def words():
    page = request.args.get('page', 1, type=int)
    book_id = request.args.get('book', 0, type=int)
    lesson_number = request.args.get('lesson', 0, type=int)
    query = EnglishWord.query
    my_query = current_user.english_words
    book = EnglishBook.query.filter_by(id=book_id).first()
    lesson = EnglishLesson.query.filter(EnglishLesson.book_id == book.id, EnglishLesson.number == lesson_number).first()
    if book:
        query = query.join(EnglishWord.lesson).filter(EnglishLesson.book_id == book.id)
        my_query = my_query.join(EnglishMyWord.word).join(EnglishWord.lesson).filter(EnglishLesson.book_id == book.id)
    if lesson:
        query = query.join(EnglishWord.lesson).filter(EnglishLesson.number == lesson.number)
        my_query = my_query.join(EnglishMyWord.word).join(EnglishWord.lesson).filter(EnglishLesson.number == lesson.number)
    pagination = query.order_by(EnglishWord.id.asc()).paginate(
        page, per_page=current_app.config["WORDS_PER_PAGE"], error_out=False)
    my_pagination = my_query.order_by(EnglishMyWord.word_id.asc()).paginate(
        page, per_page=current_app.config["WORDS_PER_PAGE"], error_out=False)
    words = pagination.items
    my_words = my_pagination.items
    return render_template('english/words.html', words=words, pagination=pagination,
                           my_words=my_words, my_pagination=my_pagination,
                           book=book, lesson=lesson)


@english.route('/exercise/new')
@login_required
def new_exercise():
    #exercise = EnglishMyExercise.query.filter_by(user_id=current_user.id).filter(EnglishMyExercise.current<EnglishMyExercise.total).first()
    exercises = [e for e in current_user.english_exercises if e.current < e.total and e.total > 0]
    if exercises:
        return redirect(url_for('english.do_exercise', id=exercises[0].id))
    exercise = current_user.english_exercises.filter(EnglishMyExercise.total == 0).one_or_none()
    if not exercise:
        exercise = EnglishMyExercise(user_id=current_user.id, use_mask=current_user.english_setting.use_mask)
        db.session.add(exercise)
        db.session.commit()
    if exercise.id:
        exercise.generate_questions()
        if exercise.has_questions():
            return redirect(url_for('english.do_exercise', id=exercise.id))
        else:
            flash('Not enough words to generate an exercise.')
            return redirect(url_for('english.exercises'))
    abort(500)


@english.route('/exercise/<int:id>', methods=['GET', 'POST'])
@login_required
def do_exercise(id):
    q = request.args.get('q', 0, type=int)
    exercise = EnglishMyExercise.query.filter_by(id=id).first()
    if exercise and exercise.current != q:
        return redirect(url_for('english.do_exercise', id=exercise.id, q=exercise.current))
    if q >= exercise.total:
        return redirect(url_for('english.evaluate_exercise', id=exercise.id))
    myword = exercise.get_question_by_index(q)['word']
    #word_id = exercise.questions.split(',')[q]
    #myword = EnglishMyWord.query.filter(and_(EnglishMyWord.user_id==exercise.user_id, EnglishMyWord.word_id==word_id)).first_or_404()
    form = QuestionForm()
    if form.validate_on_submit():
        answer = form.answer.data
        if answer == myword.word.english:
            exercise.questions_result = exercise.questions_result[0:q] + '1'
        else:
            exercise.questions_result = exercise.questions_result[0:q] + '0'
        if not exercise.questions_answer:
            exercise.questions_answer = answer
        else:
            exercise.questions_answer = ','.join([exercise.questions_answer, answer])
        exercise.current += 1
        db.session.add(exercise)
        db.session.commit()
        if exercise.current == exercise.total:
            return redirect(url_for('english.evaluate_exercise', id=exercise.id))
        return redirect(url_for('english.do_exercise', id=exercise.id, q=exercise.current))
    form.word_mask.data = myword.mask(exercise.id * 100 + q, use_mask=exercise.use_mask)
    return render_template('english/do_exercise.html', form=form, exercise=exercise, myword=myword)


@english.route('/exercise/evaluate/<int:id>')
@login_required
def evaluate_exercise(id):
    exercise = EnglishMyExercise.query.filter_by(id=id).first_or_404()

    # if exercise is not finished
    if exercise and exercise.total != exercise.current:
        return redirect(url_for('english.do_exercise', id=id, q=exercise.current))
    elif not exercise.finish_dt:
        exercise.passed = 0
        for index, question in enumerate(exercise.get_questions()):
            myword = question['word']
            myword.tested += 1
            if question['result'] == '1':
                myword.passed += 1
                exercise.passed += 1
            db.session.add(myword)
        exercise.finish_dt = datetime.utcnow()
        db.session.add(exercise)
        db.session.commit()
    return redirect(url_for('english.exercise_result', id=id))


@english.route('/exercises')
@login_required
def exercises():
    page = request.args.get('page', 1, type=int)
    query = EnglishMyExercise.query
    pagination = query.order_by(EnglishMyExercise.finish_dt.desc()).paginate(
        page, per_page=current_app.config["EXERCISES_PER_PAGE"], error_out=False)
    exercises = pagination.items
    return render_template('english/exercise_results.html', exercise=current_user.has_unfinished_exercise(), exercises=exercises, pagination=pagination)


@english.route('/exercise/result/<int:id>')
@login_required
def exercise_result(id):
    exercise = EnglishMyExercise.query.filter_by(id=id).first_or_404()
    return render_template('english/exercise_result.html', exercise=exercise)


@english.route('/achievements')
@login_required
def achievements():
    achievement = {}
    if len(current_user.english_exercises.filter(EnglishMyExercise.current >= EnglishMyExercise.total, EnglishMyExercise.total > 0).all()) > 0:
        achievement['total_exercises'] = len([e for e in current_user.english_exercises if e.current >= e.total and e.total > 0])
        achievement['total_tested'] = sum([e.total for e in current_user.english_exercises if e.current >= e.total and e.total > 0])
        achievement['total_passed'] = sum([e.passed for e in current_user.english_exercises if e.current >= e.total and e.total > 0])
        achievement['total_full_score'] = len([e for e in current_user.english_exercises if e.current >= e.total and e.total > 0 and e.passed == e.total])
        achievement['highest_score'] = max([e.passed * 1. /e.total for e in current_user.english_exercises if e.current >= e.total and e.total > 0])
    if len(current_user.english_words.all()) > 0:
        achievement['total_tested_words'] = len([w for w in current_user.english_words if w.tested > 0])
        achievement['total_passed_words'] = len([w for w in current_user.english_words if w.passed > 0])
        achievement['total_words'] = len(current_user.english_words.all())
        achievement['level1_words'] = len([w for w in current_user.english_words if w.level == 1])
        achievement['level2_words'] = len([w for w in current_user.english_words if w.level == 2])
        achievement['level3_words'] = len([w for w in current_user.english_words if w.level == 3])
        achievement['level4_words'] = len([w for w in current_user.english_words if w.level == 4])
        achievement['level5_words'] = len([w for w in current_user.english_words if w.level == 5])

    return render_template('english/achievements.html', achievement=achievement)


@english.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = LevelSettingForm()
    setting = EnglishSetting.query.filter_by(user_id=current_user.id).one_or_none()
    if not setting:
        setting = EnglishSetting(user_id=current_user,
                                 total=current_app.config["WORDS_PER_EXERCISE"][0],
                                 level1=current_app.config["WORDS_PER_EXERCISE"][1],
                                 level2=current_app.config["WORDS_PER_EXERCISE"][2],
                                 level3=current_app.config["WORDS_PER_EXERCISE"][3],
                                 level4=current_app.config["WORDS_PER_EXERCISE"][4],
                                 level5=current_app.config["WORDS_PER_EXERCISE"][5])
        db.session.add(setting)
        db.commit()
    if form.validate_on_submit():
        setting.total = int(form.total.data)
        setting.level1 = int(form.level1.data)
        setting.level2 = int(form.level2.data)
        setting.level3 = int(form.level3.data)
        setting.level4 = int(form.level4.data)
        setting.level5 = int(form.level5.data)
        setting.fill_down = form.fill_down.data
        setting.fill_level5 = form.fill_level5.data
        setting.use_mask = form.use_mask.data
        db.session.add(setting)
        db.session.commit()
        flash('Settings saved.')
    form.total.data = str(setting.total)
    form.level1.data = str(setting.level1)
    form.level2.data = str(setting.level2)
    form.level3.data = str(setting.level3)
    form.level4.data = str(setting.level4)
    form.level5.data = str(setting.level5)
    form.fill_down.data = setting.fill_down
    form.fill_level5.data = setting.fill_level5
    form.use_mask.data = setting.use_mask
    return render_template("english/settings.html", form=form)


@english.route("/books")
@login_required
def books():
    mybooks = current_user.english_books
    books = EnglishBook.query.filter(not_(EnglishBook.id.in_([x.book_id for x in mybooks]))).order_by(EnglishBook.id).all()
    return render_template("english/books.html", mybooks=mybooks, books=books)


@english.route("/add-book/<int:id>")
@login_required
def add_book(id):
    mybooks = [x for x in current_user.english_books if x.book_id == id]
    if mybooks and mybooks[0]:
        mybook = mybooks[0]
    else:
        mybook = EnglishMyBook(book_id=id, user_id=current_user.id, selected=True)
        db.session.add(mybook)
        db.session.commit()
    if mybook:
        mybook.add_words()
    return redirect(url_for('english.books'))


@english.route("/book/<int:id>")
@login_required
def view_book(id):
    mybook = EnglishMyBook.query.filter(and_(EnglishMyBook.book_id == id, EnglishMyBook.user_id == current_user.id)).first()
    if not mybook:
        book = EnglishBook.query.filter(EnglishBook.id == id).first_or_404()
        lessons = book.lessons
    else:
        book = mybook.book
        lessons = mybook.book.lessons
    return render_template("english/book.html", mybook=mybook, book=book, lessons=lessons)


@english.route("/help")
@login_required
def help():
    return render_template("english/help.html")