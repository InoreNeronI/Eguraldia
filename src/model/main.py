
from hashlib import md5

from flask_security.core import AnonymousUser
from flask_security.models.fsqla_v2 import FsModels, FsRoleMixin, FsUserMixin
from flask_security.utils import hash_password
from sqlalchemy.orm import backref, relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String

from util.extensions import db

# Define models
FsModels.set_db_info(appdb=db)


# @see https://stackoverflow.com/a/19275188
class Anonymous(AnonymousUser):
    def __init__(self):
        super(Anonymous, self).__init__()
        self.email = 'guest@guest.net'
        self.password = 'guest_secret'


class Gravatar(object):
    """
    Simple object for create gravatar link.
    @see http://packages.python.org/Flask-Gravatar
    @see https://github.com/toway/pypress-tornado/blob/master/pypress/helpers.py#L61-L122
    gravatar = Gravatar(
    size=100,
    rating='g',
    default='retro',
    force_default=False,
    force_lower=False
    )
    :param size: Default size for avatar
    :param rating: Default rating
    :param default: Default type for unregistered emails
    :param force_default: Build only default avatars
    :param force_lower: Make email.lower() before build link
    """
    def __init__(self, size=100, rating='g', default='mm', force_default=False, force_lower=False):

        self.size = size
        self.rating = rating
        self.default = default
        self.force_default = force_default
        self.force_lower = force_lower

    def __call__(self, email, size=None, rating=None, default=None, force_default=None, force_lower=False):

        """Build gravatar link."""

        if size is None:
            size = self.size

        if rating is None:
            rating = self.rating

        if default is None:
            default = self.default

        if force_default is None:
            force_default = self.force_default

        if force_lower is None:
            force_lower = self.force_lower

        if force_lower:
            email = email.lower()

        hash = md5(email.encode('utf-8')).hexdigest()

        link = 'http://www.gravatar.com/avatar/{hash}?s={size}&d={default}&r={rating}'.format(**locals())

        if force_default:
            link = link + '&f=y'

        return link


class Mail(db.Model):
    __tablename__ = 'e_mails'

    email = Column(type_=String, nullable=False, unique=True)
    user_id = Column(ForeignKey('user.id'), type_=Integer, nullable=False)

    def __init__(self, email, user):
        self.email = email.lower()
        self.user_id = user.id


# @see https://flask-security-too.readthedocs.io/en/stable/quickstart.html#id4
class Role(db.Model, FsRoleMixin):
    __tablename__ = 'role'

    def __init__(self, name, **kwargs):
        db.Model.__init__(self, name=name.upper(), **kwargs)

    @classmethod
    def get_by_name(cls, name):
        """Get record by name"""
        return cls.query.filter_by(name=name.upper()).one()

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<Role({self.name})>"


class Text(db.Model):
    __tablename__ = 'text'

    id = Column(type_=String, nullable=False, primary_key=True)
    text = Column(type_=String, nullable=False)

    def __init__(self, hash, text):
        self.id = hash
        self.text = text

    def __repr__(self):
        """Represent instance as a unique string."""
        return "<Text('%s', '%s')>" % (self.id, self.text)


# @see https://stackoverflow.com/a/37473078
class User(db.Model, FsUserMixin):
    __tablename__ = 'user'

    first_name = Column(type_=String(100))
    last_name = Column(type_=String(100))
    password = Column(type_=String(255), nullable=True)
    provider = Column(type_=String(100), nullable=True)

    emails = relationship(Mail, backref=backref('user'), lazy='dynamic')

    def __init__(self, email, password=None, username=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, email=email.lower(), password=hash_password(password=password),
                          **kwargs)
        self.set_username(username)

    def avatar(self, size):
        """Get Gravatar."""
        gravatar = Gravatar(size=size, force_lower=True)
        return gravatar(email=self.email)

    @property
    def full_name(self):
        """Get fullname."""
        return f"{self.first_name} {self.last_name}"

    def set_username(self, username):
        """Set username."""
        calc = self.calc_username()  # TODO: manage duplicates
        self.username = username.lower() if username else calc[:calc.index('@')]

    # @see https://stackoverflow.com/a/12918081
    def __repr__(self):
        """Represent instance as a unique string."""
        return "<User('%d', '%s', '%s')>" % (self.id, self.username, self.email)

    def __eq__(self, other):
        """
        Checks the equality of two `FsUserMixin` objects using `get_id`.
        """
        if isinstance(other, FsUserMixin):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        """
        Checks the inequality of two `FsUserMixin` objects using `get_id`.
        """
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal


# @see https://stackoverflow.com/a/2587041
def get(model, **kwargs):
    return db.session.query(model).filter_by(**kwargs).one_or_none()
