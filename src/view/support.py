
from flask.globals import current_app
from flask.helpers import flash
from flask_babel import _
from flask_mail import Message

from controller.main import render
from form.support import SupportForm
from model.main import User
from util.extensions import db, mail


# @see https://stackoverflow.com/a/13587339
# @see https://web.archive.org/web/20190627070834/http://flask.pocoo.org/snippets/12
# @see https://stackoverflow.com/questions/19152471/what-is-the-technique-of-presenting-again-form-which-contains-error
@current_app.route('/support', methods=('GET', 'POST'))
def support():
    """Support view"""
    form = SupportForm()
    if form.validate_on_submit():
        admin_users = db.session.query(User).filter(User.roles.any(name='ROLE_ADMIN')).all()
        sender = '%s <%s>' % (form.name.data, form.email.data)
        mail.send(message=Message(
            body=form.message.data,
            recipients=[user.email for user in admin_users],
            reply_to=form.email.data,
            sender=sender,
            subject=_('Message from %s') % sender
        ))
        flash(_('Your message has been sent. Thank you!'), 'success')

    return render(template_name_or_list='__support.html', form=form)
