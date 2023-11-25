
from datetime import datetime

from model.main import Anonymous, Role
from util.db import store

guest = Anonymous()
store.create_role(description='Administrator role', name='ROLE_ADMIN')
store.create_role(description='User role', name='ROLE_USER')
admin = store.create_user(confirmed_at=datetime.now(), email='ez.g.ur.aldia@gmail.com',
                          password='admin_secret', roles=[Role.get_by_name('ROLE_ADMIN')])
user = store.create_user(confirmed_at=datetime.now(), email='martinmozos@gmail.com',
                         password='user_secret', roles=[Role.get_by_name('ROLE_USER')])
guest = store.create_user(confirmed_at=datetime.now(), email=guest.email,
                          password=guest.password, roles=guest.roles)
