from sqlalchemy import Column, String
from main_db import *
from _utils import *

class users_sudo_db(BASE):
    __tablename__ = "users_sudo"
    user_id = Column(String(14), primary_key=True)

    def __init__(self, user_id):
        self.user_id = user_id


users_sudo_db.__table__.create(checkfirst=True)

@run_in_exc
def is_users_sudo(user_id):
    if not str(user_id).isdigit:
        return
    try:
        return SESSION.query(users_sudo_db).filter(users_sudo_db.user_id == str(user_id)).one()
    except:
        return None
    finally:
        SESSION.close()

@run_in_exc
def add_user_(user_id):
    adder = users_sudo_db(str(user_id))
    SESSION.add(adder)
    SESSION.commit()

@run_in_exc
def rm_user(user_id):
    if rem := SESSION.query(users_sudo_db).get(str(user_id)):
        SESSION.delete(rem)
        SESSION.commit()

@run_in_exc
def get_all_users_sudo():
    rem = SESSION.query(users_sudo_db).all()
    SESSION.close()
    return rem