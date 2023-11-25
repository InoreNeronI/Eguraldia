
from flask_babel import _
from flask_wtf.form import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms.fields import EmailField, StringField
from wtforms.fields.simple import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class SupportForm(FlaskForm):
    """Support form."""
    name = StringField(label=_('Name'), validators=[Length(max=35), DataRequired()])
    email = EmailField(label=_('Email Address'), validators=[Length(min=6, max=120), Email()])
    message = TextAreaField(label=_('Message'), validators=[Length(max=1000), DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField(label=_('Send'))
