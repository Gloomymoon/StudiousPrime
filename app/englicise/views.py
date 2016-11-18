from datetime import datetime
from flask import render_template, flash, request, current_app, redirect, url_for, abort
from flask_login import login_required, current_user
from . import englicise
from app import db
from .forms import NewWordForm, EditWordForm, QuestionForm
from .models import EnglishWord, EnglishWordScore, EnglishExercise, EnglishQuestion, EnglishBook, EnglishStatistic


@englicise.route('/')
@login_required
def index():
    words = EnglishStatistic.wrong_words(current_user.id, 5)
    return render_template('englicise/index.html', words=words)


@englicise.route('/add-word', methods=['GET', 'POST'])
@login_required
def add_word():
    back_href = request.args.get('back', '', type=str)
    if not back_href:
        back_href = url_for('englicise.words')
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
        ws = EnglishWordScore.query.filter_by(word_id=word.id).filter_by(user_id=current_user.id).first()
        if not ws:
            ws = EnglishWordScore(word_id=word.id, user_id=current_user.id)
            db.session.add(ws)
            db.session.commit()
            flash('New word [' + word.english + '] has been added.')
        else:
            flash('Word [' + word.english + '] already added.')
    return render_template('englicise/add_word.html', form=form, back_href=back_href)


@englicise.route('/word/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_word(id):
    back_href = request.args.get('back', '', type=str)
    if not back_href:
        back_href = url_for('englicise.words')
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
    return render_template('englicise/edit_word.html', form=form, back_href=back_href)


@englicise.route('/words')
@login_required
def words():
    page = request.args.get('page', 1, type=int)
    query = EnglishWord.query
    pagination = query.order_by(EnglishWord.id.desc()).paginate(
        page, per_page=current_app.config["WORDS_PER_PAGE"], error_out=False)
    words = pagination.items
    return render_template('englicise/words.html', words=words, pagination=pagination)


@englicise.route('/exercise')
@login_required
def exercise():
    exercise = EnglishExercise.query.filter_by(user_id=current_user.id).filter(EnglishExercise.current<EnglishExercise.total).first()
    if exercise:
        return redirect(url_for('englicise.do_exercise', id=exercise.id))
    exercise = EnglishExercise(user_id=current_user.id)
    db.session.add(exercise)
    db.session.commit()
    if exercise.id:
        exercise.generate_questions()
        return redirect(url_for('englicise.do_exercise', id=exercise.id))
    abort(500)


@englicise.route('/exercise/<int:id>', methods=['GET', 'POST'])
@login_required
def do_exercise(id):
    q = request.args.get('q', 0, type=int)
    exercise = EnglishExercise.query.filter_by(id=id).first_or_404()
    if exercise and exercise.current != q:
        return redirect(url_for('englicise.do_exercise', id=exercise.id, q=exercise.current))
    if q >= exercise.total:
        return redirect(url_for('englicise.evaluate', id=exercise.id))
    question = EnglishQuestion.query.filter_by(exc_id=id).filter_by(index=q).first_or_404()
    form = QuestionForm()
    if form.validate_on_submit():
        question.answer = form.word_mask.data
        if question.answer == question.word.english:
            question.result = 1
        else:
            question.result = -1
        exercise.current += 1
        db.session.add(question)
        db.session.add(exercise)
        db.session.commit()
        if exercise.current == exercise.total:
            return redirect(url_for('englicise.evaluate', id=exercise.id))
        return redirect(url_for('englicise.do_exercise', id=exercise.id, q=exercise.current))
    return render_template('englicise/do_exercise.html', form=form, exercise=exercise, question=question)


@englicise.route('/evaluate/<int:id>')
@login_required
def evaluate(id):
    exercise = EnglishExercise.query.filter_by(id=id).first_or_404()

    # if exercise is not finished
    if exercise and exercise.total != exercise.current:
        return redirect(url_for('englicise.do_exercise', id=id, q=exercise.current))

    # if exercise has already been evaluated
    if exercise.finish:
        flash('This exercise has already been evaluated.')
    elif exercise.total == exercise.current:
        correct = 0
        wordscores = EnglishWordScore.query.filter_by(user_id=exercise.user_id)
        for question in exercise.questions:
            ws = wordscores.filter_by(word_id=question.word_id).first()
            if not ws:
                ws = EnglishWordScore(user_id=exercise.user_id, word_id=question.word_id)
            if question.result == 1:
                correct += 1
                ws.score += 1
            db.session.add(ws)
        exercise.correct = correct
        exercise.finish = datetime.utcnow()
        db.session.add(exercise)
        db.session.commit()
    return redirect(url_for('englicise.exercise_result', id=id))


@englicise.route('/results')
@login_required
def exercise_results():
    page = request.args.get('page', 1, type=int)
    query = EnglishExercise.query
    pagination = query.order_by(EnglishExercise.finish.desc()).paginate(
        page, per_page=current_app.config["EXERCISES_PER_PAGE"], error_out=False)
    exercises = pagination.items
    return render_template('englicise/exercise_results.html', exercises=exercises, pagination=pagination)


@englicise.route('/result/<int:id>')
@login_required
def exercise_result(id):
    exercise = EnglishExercise.query.filter_by(id=id).first_or_404()
    return render_template('englicise/exercise_result.html', exercise=exercise)

@englicise.route('/achievements')
@login_required
def achievements():
    achievements = EnglishStatistic.achievements(current_user.id)
    return render_template('englicise/achievements.html', achievements=achievements)