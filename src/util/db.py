"""Database module, including the SQLAlchemy database object and DB-related utilities."""

from flask_security.datastore import SQLAlchemyUserDatastore
from sqlalchemy.schema import Column, ForeignKey

from model.main import Role, User
from util.extensions import db

store = SQLAlchemyUserDatastore(db=db, role_model=Role, user_model=User)


def reference_col(table_name, nullable=False, pk_name='id',
                  foreign_key_kwargs=None, column_kwargs=None):
    """Column that adds primary key foreign key reference.
    Usage: ::
        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    foreign_key_kwargs = foreign_key_kwargs or {}
    column_kwargs = column_kwargs or {}

    return Column(
        ForeignKey(f"{table_name}.{pk_name}", **foreign_key_kwargs),
        nullable=nullable,
        **column_kwargs,
    )
