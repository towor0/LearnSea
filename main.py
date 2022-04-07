from flask import Flask, render_template, request, redirect, url_for, abort
from flask_login import UserMixin, LoginManager, login_required, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from forms import *
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__, static_folder="static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///myDB.db"
app.config["SECRET_KEY"] = "17013e9e65ccfc1bd085fa7cd5626bada171beb0"
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=128), nullable=False)
    role = db.Column(db.String(length=16), nullable=True)
    joined_at_date = db.Column(db.DateTime(), index=True, default=datetime.utcnow())
    tutors = db.relationship("Tutor", back_populates="user")
    videos = db.relationship("Video", back_populates="user")

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)


class Subject(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=50), nullable=False, unique=True)
    description = db.Column(db.String(length=16), nullable=True)
    image = db.Column(db.String(length=128), nullable=False)


class Tutor(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=50), nullable=False)
    subject = db.Column(db.String(length=128), nullable=True)
    email = db.Column(db.String(length=128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="tutors")


class Video(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(length=50), nullable=False)
    description = db.Column(db.String(length=5000))
    subject = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="videos")


@app.route('/')
@app.route('/home')
@login_required
def home():
    subjects = Subject.query.all()
    return render_template("home.html", subjects=subjects)


@app.route("/subject/<subjectName>", methods=["POST", "GET"])
@login_required
def subject(subjectName):
    if Subject.query.filter_by(name=subjectName).first() is None:
        abort(404)
    videos = Video.query.filter_by(subject=subjectName).all()
    search = VideoSearchForm()
    if search.validate_on_submit():
        videos_filter = []
        for video in videos:
            if search.search.data.lower() in video.title.lower():
                videos_filter.append(video)
        return render_template("subject.html", videos=videos_filter, form=search)
    return render_template("subject.html", videos=videos, form=search)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html", form=form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegisterForm()
    if form.validate_on_submit() and form.username.data.isalnum():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        if User.query.filter_by(username=form.username.data).first():
            return redirect(url_for('exist'))
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("signup.html", form=form)


@app.route('/exist')
def exist():
    return "Account already exist"


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    video_form = VideoForm()
    subjects = Subject.query.all()
    subjectsName = []
    for subject in subjects:
        subjectsName.append((subject.name, subject.name.capitalize()))
    video_form.subject.choices = subjectsName
    if video_form.validate_on_submit():
        if not Video.query.filter_by(title=video_form.title.data, user=current_user).first():
            video = Video(title=video_form.title.data, description=video_form.description.data,
                          subject=video_form.subject.data, user=current_user)
            db.session.add(video)
            db.session.commit()
            filetype = secure_filename(video_form.video.data.filename).split(".")[-1]
            video_form.video.data.save(
                'static/video/' + current_user.username + "." + video.title + "." + filetype)
            filetype = secure_filename(video_form.material.data.filename).split(".")[-1]
            video_form.material.data.save(
                'static/material/' + current_user.username + "." + video.title + "." + filetype)
            return redirect(url_for("home"))
        else:
            return "no"
    return render_template("upload.html", video_form=video_form)


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if current_user.role != "admin":
        return redirect(url_for("home"))
    subject_form = SubjectForm()
    if subject_form.validate_on_submit():
        subject = Subject.query.filter_by(name=subject_form.name.data.lower()).first()
        if subject:
            if os.path.isfile("static/assets/" + subject.image):
                os.remove("static/assets/" + subject.image)
            filetype = secure_filename(subject_form.image.data.filename).split(".")[-1]
            subject.description = subject_form.description.data
            subject.image = subject.name + "." + filetype
        else:
            filetype = secure_filename(subject_form.image.data.filename).split(".")[-1]
            subject = Subject(name=subject_form.name.data.lower(), description=subject_form.description.data, image=subject_form.name.data.lower()+"."+filetype)
            db.session.add(subject)
        db.session.commit()
        subject_form.image.data.save('static/assets/' + subject.name + "." + filetype)
        return redirect(url_for("admin"))
    user_form = UserForm()
    if user_form.validate_on_submit():
        user = User.query.filter_by(username=user_form.username.data).first()
        if user:
            user.set_password(user_form.password.data)
        else:
            user = Subject(username=user_form.username.data)
            user.set_password(user_form.password.data)
            db.session.add(user)
        db.session.commit()
        return redirect(url_for("admin"))
    video_form = VideoForm()
    subjects = Subject.query.all()
    subjectsName = []
    for subject in subjects:
        subjectsName.append((subject.name, subject.name.capitalize()))
    video_form.subject.choices = subjectsName
    if video_form.validate_on_submit():
        video = Video(title=video_form.title.data, description=video_form.description.data,
                      subject=video_form.subject.data, user=current_user)
        db.session.add(video)
        db.session.commit()
        filetype = secure_filename(video_form.video.data.filename).split(".")[-1]
        video_form.video.data.save(
            'static/video/' + current_user.username + "." + video.title + "." + filetype)
        filetype = secure_filename(video_form.material.data.filename).split(".")[-1]
        video_form.material.data.save(
            'static/material/' + current_user.username + "." + video.title + "." + filetype)
        return redirect(url_for("home"))
    return render_template("admin.html", user_form=user_form, subject_form=subject_form, video_form=video_form)


@app.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    videos = Video.query.filter_by(user=user).order_by(Video.id.desc()).all()
    if len(videos) > 4:
        videos = videos[:4]
    tutors = Tutor.query.filter_by(user=user).all()
    if not user:
        abort(404)
    return render_template("user.html", user=user, tutors=tutors, videos=videos)


@app.route("/tutor", methods=["GET", "POST"])
@login_required
def tutor():
    tutors = Tutor.query.all()
    subjectsName = [(subject.name, subject.name.capitalize()) for subject in Subject.query.all()]
    form = TutorForm()
    form.subject.choices = subjectsName
    if form.validate_on_submit():
        tutor = Tutor(name=form.name.data, subject=form.subject.data, email=form.email.data, user=current_user)
        db.session.add(tutor)
        db.session.commit()
        return redirect(url_for("tutor"))
    return render_template("tutor.html", tutors=tutors, form=form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
