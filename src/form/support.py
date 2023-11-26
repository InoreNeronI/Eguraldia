
from flask_babel import lazy_gettext
from flask_wtf.form import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms.fields import EmailField, StringField
from wtforms.fields.simple import SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class SupportForm(FlaskForm):
    """Support form."""
    name = StringField(label=lazy_gettext('Name'), validators=[Length(max=35), DataRequired()])
    email = EmailField(label=lazy_gettext('Email Address'), validators=[Length(min=6, max=120), Email()])
    message = TextAreaField(label=lazy_gettext('Message'), validators=[Length(max=1000), DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField(label=lazy_gettext('Send'))
