from datetime import datetime

from flask import render_template, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import redirect

from app import app, login_manager, bcrypt, db
from flask import abort
from .models import User, Event
from .forms import UserAuthForm, EventForm


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserAuthForm()
    if form.validate_on_submit():
        user = User.query.get(form.email.data)
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=True)
            return redirect('/')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def create_user():
    form = UserAuthForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')
        test_user = User.query.get(email)
        if test_user:
            abort(409)
        user = User(email=email, password=bcrypt.generate_password_hash(password).decode('utf-8'))
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/add-event', methods=['GET', 'POST'])
@login_required
def add_event():
    form = EventForm()
    if form.validate_on_submit():
        title = request.form.get('title')
        desc = request.form.get('desc')
        time_start = request.form.get('time_start')
        time_end = request.form.get('time_end')
        if (time_end <= time_start) or (datetime.strptime(time_end, '%Y-%m-%dT%H:%M') <= datetime.now()):
            message = 'Wrong event time!'
            return render_template('add-event.html', form=form, message=message)
        event = Event(author=current_user.email, title=title, desc=desc, time_start=time_start, time_end=time_end)
        db.session.add(event)
        db.session.commit()
        return redirect('/')
    return render_template('add-event.html', form=form)


@app.route('/events-list')
@login_required
def events_list():
    events = Event.query.all()
    for event in events:
        if datetime.now() >= event.time_end:
            db.session.delete(event)
            db.session.commit()
    return render_template('events-list.html', events=events)


@app.route('/event-detail/<int:event_id>', methods=['GET', 'POST'])
@login_required
def event_detail(event_id):
    event = Event.query.get(event_id)
    form = EventForm()
    if event:
        if current_user.is_authenticated:
            if event.author == current_user.email:
                if form.validate_on_submit():
                    title = request.form.get('title')
                    desc = request.form.get('desc')
                    time_start = request.form.get('time_start')
                    time_end = request.form.get('time_end')
                    if (time_end <= time_start) or (datetime.strptime(time_end, '%Y-%m-%dT%H:%M') <= datetime.now()):
                        message = 'Wrong event time!'
                        return render_template('event-detail.html', event=event, form=form, message=message)
                    event.title = title
                    event.desc = desc
                    event.time_start = time_start
                    event.time_end = time_end
                    db.session.commit()
                    return redirect('/')
        return render_template('event-detail.html', event=event, form=form)
    return abort(404)
