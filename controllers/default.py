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

def create_proposal():
    if not auth.is_logged_in():
        redirect(URL('user/login'))

    rows = db(db.proposal.owner_ == auth.user.id).select(db.proposal.ALL).as_list()
    if len(rows) > 0:
        # FIXME For now, only one proposal is permitted for each user.
        redirect(URL('index'))

    if request.env.request_method == 'POST':
        # We have multiple investigators, and the view writer can just set multiple input entry with name, say, 'first_name'. All inputs will form a Python list in the request object.
        _vars = request.vars
        _vars.owner_ = auth.user.id
        _vars.investigators = json.dumps(zip(_vars.first_name or [], _vars.last_name or [], _vars.organization or [], _vars.email or []))
        _vars.checklist = json.dumps([])
        _vars = { (k, getattr(_vars, k)) for k in _vars if k in db.proposal.fields and k != 'id' }
        db.proposal.insert(**_vars)
        redirect(URL('index'))

    # Requires 'title', 'funding_agency', 'due_date' as strings.
    # Optionally requires first_name, last_name, organization and email as investigator information.
    return dict()

def update_proposal():
    if not auth.is_logged_in():
        redirect(URL('user/login'))

    rows = db(db.proposal.owner_ == auth.user.id).select(db.proposal.ALL)
    if len(rows) == 0:
        redirect(URL('index'))
    _vars = Storage(rows[0])

    if request.env.request_method == 'POST':
        _vars = request.vars
        _vars.investigators = json.dumps(zip(_vars.first_name or [], _vars.last_name or [], _vars.organization or [], _vars.email or []))
        _vars.checklist = json.dumps([])
        _vars = { (k, getattr(_vars, k)) for k in _vars if k in db.proposal.fields and k != 'id' }
        db(db.proposal.id == row['id']).update(**_vars)
        redirect(URL('index'))

    investigators = json.loads(_vars.investigators)
    s = set(json.loads(_vars.checklist))
    _vars.checklist = s
    _vars.investigators = None
    _vars.first_name = [ x[0] for x in investigators ]
    _vars.last_name = [ x[1] for x in investigators ]
    _vars.organization = [ x[2] for x in investigators ]
    _vars.email = [ x[3] for x in investigators ]

    # The view writer needs vars for initial values.
    # print(_vars) for details
    return dict(_vars = _vars)
