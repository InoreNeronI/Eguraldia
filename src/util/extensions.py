"""Extensions module. Each one is initialized in the app factory located in flask.py."""

from datetime import datetime

from flask_alchemydumps import AlchemyDumps
from flask_babel import Babel
from flask_mail import Mail
from flask_migrate import Migrate
from flask_security.core import Security
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime, Integer

from util.translator import GoogleTranslator

db_declarative_base = declarative_base()
defaults = {}


# @see https://github.com/cookiecutter-flask/cookiecutter-flask/blob/master/{{cookiecutter.app_name}}/{{cookiecutter.app_name}}/database.py
class CRUDMixin(Model):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()

    @classmethod
    def get_or_create(cls, defaults=None, **kwargs):
        try:
            return db.session.query(cls).filter_by(**kwargs).one(), False

        except db.exc.NoResultFound:
            if defaults:
                kwargs.update(defaults)
            instance = cls(**kwargs)
            try:
                db.session.add(instance)
                db.session.flush()

                return instance, True
            except db.exc.FlushError:
                db.session.rollback()

                return db.session.query(cls).filter_by(**kwargs).one(), True


class PkModel(CRUDMixin, db_declarative_base):
    __abstract__ = True  # @see https://stackoverflow.com/a/50057537

    id = Column(Integer, autoincrement=True, primary_key=True)
    create_datetime = Column(type_=DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(type_=DateTime, nullable=False, server_default=func.now(),
                             onupdate=datetime.now())

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID"""
        if any((
            isinstance(record_id, (str, bytes)) and record_id.isdigit(),
            isinstance(record_id, (int, float)),
        )):
            return cls.query.get(int(record_id))
        return None

    def get_columns(self):
        """ Get column names"""
        # @see https://stackoverflow.com/q/1958219/1960546#comment12704240_1960546
        return dict((col, getattr(self, col)) for col in self.__table__.columns.keys())


alchemydumps = AlchemyDumps()
babel = Babel()
db = SQLAlchemy(model_class=PkModel)
db_declarative_base.query = db.session.query_property()
mail = Mail()
migrator = Migrate()
security = Security()
# @see https://github.com/ssut/py-googletrans/issues/234#issuecomment-733178073
translator = GoogleTranslator(timeout=0.25)
