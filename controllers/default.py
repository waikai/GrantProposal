# -*- coding: utf-8 -*-

def index():
    if not auth.is_logged_in(): # more permission checking in the future
        redirect(URL('user/login'))
    return dict(locals())

def user():
    form = auth()
    return dict(locals())

def create_proposal():
    form = crud.create(db.proposal)
    return dict(locals())
