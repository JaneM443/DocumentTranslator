
from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField


class RegistrationForm(FlaskForm):
    username = StringField('Username', render_kw={"placeholder": "Enter Username"})
    password = PasswordField('Password',render_kw={"placeholder": "Enter Password"})
    confirm_password = PasswordField('Confirm Password', render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', render_kw={"placeholder": "Enter Username"})
    password = PasswordField('Password', render_kw={"placeholder": "Enter Password"})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UploadForm(FlaskForm):
    file = StringField('File', render_kw={"placeholder": "Enter file id"})
    method = SelectField('Method', choices=[('Overwrite'),('New Version'),('Add Content'),('Delete Content')])
    submit = SubmitField('Upload')

class ExportForm(FlaskForm):
    type = SelectField('Type', choices=[('Google Sheets'),('Google Doc')])
    submit = SubmitField('Export')

class ProjectForm(FlaskForm):
    search = StringField('Search', render_kw={"placeholder": "Search"})
    submit = SubmitField('Browse')

class ReadonlyStringField(StringField):
  def __call__(self, *args, **kwargs):
    kwargs.setdefault('readonly', True)
    return super(ReadonlyStringField, self).__call__(*args, **kwargs)

class EditForm(FlaskForm):
    type = SelectField('Type', choices=[('Text'),('Video'),('Choice')])
    title = StringField('Title', render_kw={"placeholder": "Title"})
    body = StringField('Body', render_kw={"placeholder": "Body"})
    overlap = IntegerField('Overlap', render_kw={"placeholder": "Overlap"})
    file = StringField('File Name', render_kw={"placeholder": "File Name"})
    vtt = StringField('VTT Name', render_kw={"placeholder": "VTT Name"})
    id = ReadonlyStringField('ID')
    submit = SubmitField('Save Changes')
    
