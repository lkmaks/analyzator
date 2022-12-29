from app import app, db
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user
from app.models import User, Room, TemporaryUser
from app.forms import LoginForm, RegistrationForm, KeywordForm
from werkzeug.urls import url_parse
from flask_socketio import join_room
import os


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', rooms=Room.query.all())


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign in', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, is_admin=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=True)
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)


@app.route('/room', methods=['GET', 'POST'])
def room():
    if not current_user.is_authenticated:
        return redirect(url_for('login', next=request.full_path))
    if request.method == 'GET':
        room_id = request.args.get('id')
        if TemporaryUser.query.filter_by(user_id=current_user.id, room_id=room_id).first() is None \
            and room_id != None:
            tu = TemporaryUser(room_id=room_id, user=current_user)
            db.session.add(tu)
            db.session.commit()
        return render_template('room.html', title='Room {}'.format(room_id),
                               temp_users=TemporaryUser.query.filter_by(room_id=room_id).all())


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))



@app.route('/create_room', methods=['POST'])
def create_room():
    if current_user.is_authenticated:
        room = Room(position='')
        db.session.add(room)
        db.session.commit()
        return str(room.id)
    return 'ti cho tipa hitry ochen?'


@app.route('/become_admin', methods=['GET', 'POST'])
def become_admin():
    if current_user.is_authenticated:
        print('user!!!!!!!')
        form = KeywordForm()
        if request.method == 'GET':
            return render_template('become_admin.html', title='GIVE ME POWER', form=form)
        elif request.method == 'POST':
            if form.validate_on_submit():
                print('form')
                key = form.data['keyword']
                print(key)
                if key == 'k3rnel-pan1c':
                    print('pass')
                    current_user.is_admin = 1
                    db.session.add(current_user)
                    db.session.commit()
                    return redirect(url_for('index'))
                else:
                    return 'FAILED. WRONG KEY.'
    else:
        return redirect(url_for('register'))

