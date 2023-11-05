from flask import render_template, redirect, url_for, flash, request, session, jsonify
from app import app, db
import json
import random
from sqlalchemy import desc
from flask_login import current_user, login_user, logout_user, login_required
from forms import LoginForm, RegistrationForm, TriviaPackForm, TriviaQuestionForm, AnswerForm
from models import User, TriviaPack, Question, Scoreboard, Like

CATEGORIES = ['entertainment', 'art', 'science', 'sport', 'geography', 'history', 'custom']

@app.route('/')
@app.route('/index')
def index():

    return render_template('index.html', pack_categories=CATEGORIES)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page:
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)  # This assumes your form has a password field
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))  # Redirect to the login page after registering

    return render_template('register.html', title='Register', form=form)


@app.route('/category/<string:category_name>')
def category_view(category_name):

    # Retrieve TriviaPacks with the given title, sorted by likes
    category_packs = TriviaPack.query.filter_by(title=category_name) \
        .outerjoin(Like) \
        .group_by(TriviaPack.id) \
        .order_by(db.desc(db.func.count(Like.id))) \
        .with_entities(
        TriviaPack.id,
        TriviaPack.description,
        db.func.count(Like.id).label('likes_count')
    ) \
        .all()

    return render_template('category.html', category_name=category_name, category_packs=category_packs)


@app.route('/create_trivia_pack', methods=['GET', 'POST'])
@login_required
def create_trivia_pack():
    form = TriviaPackForm()
    if form.validate_on_submit():
        new_pack = TriviaPack(title=form.title.data, description=form.description.data, creator=current_user)
        db.session.add(new_pack)
        db.session.commit()
        # Redirect to the submit_question page with the pack_id
        return redirect(url_for('submit_trivia_question', pack_id=new_pack.id))
    return render_template('create_trivia_pack.html', form=form)


@app.route('/create_trivia_pack/<int:pack_id>/submit_question', methods=['GET', 'POST'])
@login_required
def submit_trivia_question(pack_id):
    # Get the current trivia pack by ID
    trivia_pack = TriviaPack.query.get_or_404(pack_id)

    # Check if the current user is the creator of the trivia pack
    if trivia_pack.creator_id != current_user.id:
        flash('You do not have permission to add questions to this trivia pack.')
        return redirect(url_for('home'))  # Replace 'home' with the correct endpoint for your homepage

    # Get the count of questions already in this pack
    question_count = Question.query.filter_by(pack_id=pack_id).count()

    # If 10 questions have been added, show the pack completion message
    if question_count > 4:
        return render_template('trivia_pack_completed.html')  # You'll need to create this template

    # Otherwise, proceed with question submission
    form = TriviaQuestionForm()
    if form.validate_on_submit():
        # Create a new Question object and add it to the database
        new_question = Question(content=form.content.data,
                                correct_answer=form.correct_answer.data,
                                incorrect_answers=json.dumps([
                                    form.incorrect_answer1.data,
                                    form.incorrect_answer2.data,
                                    form.incorrect_answer3.data
                                ]),
                                pack_id=pack_id)
        db.session.add(new_question)
        db.session.commit()
        # Redirect to the same page to add another question or complete the pack
        return redirect(url_for('submit_trivia_question', pack_id=pack_id))

    # Render the question submission page with the form and the current question count
    return render_template('submit_trivia_question.html', form=form, pack_id=pack_id,
                           question_number=question_count + 1)


@app.route('/list_trivia_packs')
def list_trivia_packs():
    # Fetch all trivia packs logic
    pass  # Placeholder for fetching logic
    return render_template('list_trivia_packs.html')

@app.route('/play_trivia_pack/<int:pack_id>')
@login_required
def play_trivia_pack(pack_id):
    # Get the trivia pack by ID and its questions
    trivia_pack = TriviaPack.query.get_or_404(pack_id)
    questions = Question.query.filter_by(pack_id=pack_id).all()

    # Start the game session
    session['trivia_pack_id'] = pack_id
    session['question_ids'] = [question.id for question in questions]
    session['current_question_index'] = 0
    session['score'] = 0

    # Redirect to the first question
    return redirect(url_for('question_view', question_id=session['question_ids'][0]))

@app.route('/question/<int:question_id>', methods=['GET'])
@login_required
def question_view(question_id):
    # If the session data is not set, redirect to the homepage or an error page
    if 'trivia_pack_id' not in session or 'question_ids' not in session:
        flash('No active trivia pack session found.')
        return redirect(url_for('index'))



    question = Question.query.get_or_404(question_id)
    incorrect_answers = json.loads(question.incorrect_answers)
    all_answers = incorrect_answers + [question.correct_answer]
    random.shuffle(all_answers)

    current_index = session['question_ids'].index(question_id)
    last_question_index = len(session['question_ids']) - 1

    if current_index < last_question_index:
        next_question_id = session['question_ids'][current_index + 1]
        return render_template('question.html',
                               question=question,
                               answers=all_answers,
                               correct_answer=question.correct_answer,
                               next_question_id=next_question_id)
    else:
        # This is the last question, handle accordingly
        return render_template('question.html',
                               question=question,
                               answers=all_answers,
                               correct_answer=question.correct_answer,
                               last_question=True)  # Indicate that this is the last question


@app.route('/update_score', methods=['POST'])
@login_required
def update_score():
    data = request.json
    if data['correct']:
        session['score'] += 1
    session.modified = True  # Ensure the session is marked as modified so it gets saved
    return jsonify(success=True), 200

@app.route('/trivia_results')
@login_required
def trivia_results():
    # Get the pack_id from the session
    pack_id = session.get('trivia_pack_id')

    # If there's no pack_id in the session, redirect to the homepage or an appropriate error page
    if not pack_id:
        flash('No active trivia pack session found.')
        return redirect(url_for('index'))

    pack = TriviaPack.query.get_or_404(pack_id)
    score = session.get('score', 0)
    total_questions = len(session.get('question_ids', []))

    # Check if the current user has already liked the trivia pack
    user_has_liked = Like.query.filter_by(user_id=current_user.id, pack_id=pack.id).count() > 0

    # Clear the session data for the trivia pack
    session.pop('trivia_pack_id', None)
    session.pop('question_ids', None)
    session.pop('current_question_index', None)

    return render_template('results.html', score=score, total_questions=total_questions,
                           user_has_liked=user_has_liked, pack=pack)

@app.route('/like_pack/<int:pack_id>', methods=['POST'])
@login_required
def like_pack(pack_id):
    pack = TriviaPack.query.get_or_404(pack_id)
    if not pack:
        flash('Trivia pack not found.', 'danger')
        return redirect(url_for('index'))

    like = Like.query.filter_by(user_id=current_user.id, pack_id=pack.id).first()
    if like:
        flash('You have already liked this pack.', 'info')
    else:
        like = Like(user_id=current_user.id, pack_id=pack.id)
        db.session.add(like)
        db.session.commit()
        flash('Liked trivia pack!', 'success')
    return redirect(url_for('trivia_results', pack_id=pack_id))

@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    total_likes = Like.query.filter_by(user_id=user.id).count()

    # Pass categories and total_likes to the template
    return render_template('profile.html', user=user, title=CATEGORIES, total_likes=total_likes)

@app.route('/profile/<username>/<category_name>')
@login_required
def profile_category(username, category_name):
    user = User.query.filter_by(username=username).first_or_404()
    trivia_packs = TriviaPack.query.filter_by(creator_id=user.id, title=category_name).all()

    pack_likes = {pack.id: Like.query.filter_by(pack_id=pack.id).count() for pack in trivia_packs}

    return render_template('profile_category.html', user=user, category_name=category_name, trivia_packs=trivia_packs, pack_likes=pack_likes)



@app.route('/leaderboard')
def leaderboard():
    # Assuming you have a User model and a Like model set up correctly
    leaderboard_data = User.query.outerjoin(Like, User.id == Like.user_id)\
                                  .group_by(User.id)\
                                  .order_by(db.desc(db.func.count(Like.id)))\
                                  .with_entities(User.username, db.func.count(Like.id).label('likes_count'))\
                                  .all()

    return render_template('leaderboard.html', leaderboard=leaderboard_data)



# Implement additional routes as needed

if __name__ == '__main__':
    app.run(debug=True)
