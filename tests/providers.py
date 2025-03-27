from .factories import *


def set_factories_session(db):
    for factory in (UserFactory,):
        factory._meta.sqlalchemy_session = db
