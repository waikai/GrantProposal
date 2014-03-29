# -*- coding: utf-8 -*-

import json
from gluon.storage import Storage

def index():
    if not auth.is_logged_in(): # more permission checking in the future
        redirect(URL('user/login'))
    return dict(locals())

def user():
    form = auth()
    return dict(locals())

def display_form():
    form=FORM('Your name:', INPUT(_name='name'), INPUT(_type='submit'))
    return dict(form=form)

def create_proposal():
    if not auth.is_logged_in():
        redirect(URL('user/login'))
    rows = db(db.proposal.owner_ == auth.user.id).select(db.proposal.ALL).as_list()
    if len(rows) > 0:
        # FIXME For now, only one proposal is permitted for each user.
        redirect(URL('index'))

    create_proposal = SQLFORM(db.proposal, rows)
    create_proposal.vars.owner_ = auth.user.id
    if create_proposal.process().accepted:
        redirect(URL('index'))
        response.flash = 'form accepted'
    elif create_proposal.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill out the form'
    return dict(create_proposal=create_proposal)

def update_proposal():
    if not auth.is_logged_in():
        redirect(URL('user/login'))

    rows = db.proposal[auth.user.id]
    db.proposal.id.writable = False 
    db.proposal.id.readable = False 
    db.proposal.owner_.writable = False 
    db.proposal.owner_.readable = False 
    update_proposal = SQLFORM(db.proposal, rows)
 
    investigators = SQLFORM(db.investigators)
    investigators.vars.owner_ = auth.user.id

    if update_proposal.process().accepted:
        redirect(URL('index'))
        response.flash = 'form accepted'
    elif update_proposal.errors:
        response.flash = 'form has errors'
    return dict(update_proposal=update_proposal, investigators = investigators)
