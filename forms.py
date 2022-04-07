from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, SelectField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Signup")


class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Add/Edit")


class SubjectForm(FlaskForm):
    name = StringField("Subject Name", validators=[DataRequired()])
    description = StringField("Subject Description", validators=[DataRequired()])
    image = FileField("Subject Image", validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField("Add/Edit")


class TutorForm(FlaskForm):
    name = StringField("Fullname", validators=[DataRequired()])
    subject = SelectField("Subject", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Create")


class VideoForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    video = FileField("Video", validators=[FileRequired(), FileAllowed(['mp4'], 'MP4 only!')])
    material = FileField("Material", validators=[FileRequired(), FileAllowed(['pdf'], 'PDF only!')])
    subject = SelectField("Subject", validators=[DataRequired()])
    submit = SubmitField("Upload")

class VideoSearchForm(FlaskForm):
    search = StringField("Search", validators=[DataRequired()])
    submit = SubmitField("Search")
