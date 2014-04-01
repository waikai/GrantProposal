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
        session.flash='No support for multiple proposals'
        redirect(URL('index'))

    if request.env.request_method == 'POST':
        # We have multiple investigators, and the view writer can just set multiple input entry with name, say, 'first_name'. All inputs will form a Python list in the request object.
        _vars = request.vars
        _vars.owner_ = auth.user.id
        _vars.investigators = json.dumps(zip(_vars.first_name or [], _vars.last_name or [], _vars.organization or [], _vars.email or []))
        _vars.checklist = json.dumps([])
        _vars = { k : getattr(_vars, k) for k in _vars if k in db.proposal.fields and k != 'id' }
        db.proposal.insert(**_vars)
        redirect(URL('index'))

    # Requires 'title', 'funding_agency', 'due_date' as strings.
    # Optionally requires first_name, last_name, organization and email as investigator information.
    tmp = db.proposal.fields
    tmp.remove('owner_');
    tmp.remove('investigators');
    tmp.remove('checklist');
    form = SQLFORM(db.proposal, fields=tmp)

    for option in db().select(db.checklist.name).as_list():
        form[0].insert(-1, TR(TD(LABEL(option['name']), _class='w2p_fl'), TD(INPUT(_name='checklist', _class='checkbox', _type='checkbox'), _class='w2p_fw')))

    for i in range(1, 6):
        form[0].insert(-1, TR(TD(H5('Investigator ' + str(i)), _class='w2p_fl')))
        form[0].insert(-1, TR(TD(LABEL('First Name'), _class='w2p_fl'), TD(INPUT(_name='first_name', _class='string', _type='text'), _class='w2p_fw')))
        form[0].insert(-1, TR(TD(LABEL('Last Name'), _class='w2p_fl'), TD(INPUT(_name='last_name', _class='string', _type='text'), _class='w2p_fw')))
        form[0].insert(-1, TR(TD(LABEL('Organization'), _class='w2p_fl'), TD(INPUT(_name='organization', _class='string', _type='text'), _class='w2p_fw')))
        form[0].insert(-1, TR(TD(LABEL('Email'), _class='w2p_fl'), TD(INPUT(_name='email', _class='string', _type='text'), _class='w2p_fw')))

    return dict(form=form)

def update_proposal():
    if not auth.is_logged_in():
        redirect(URL('user/login'))

    rows = db(db.proposal.owner_ == auth.user.id).select(db.proposal.ALL)
    if len(rows) == 0:
        session.flash='No proposal found. Please create a new one'
        redirect(URL('index'))
    _vars = Storage(rows[0])
    _id = _vars.id

    if request.env.request_method == 'POST':
        _vars = request.vars
        _vars.investigators = json.dumps(zip(_vars.first_name or [], _vars.last_name or [], _vars.organization or [], _vars.email or []))
        _vars.checklist = json.dumps(list(set(_vars.checklist)))
        _vars = { k : getattr(_vars, k) for k in _vars if k in db.proposal.fields and k != 'id' }
        db(db.proposal.id == _id).update(**_vars)
        redirect(URL('index'))

    investigators = json.loads(_vars.investigators)
    checklist = set(json.loads(_vars.checklist))
    first_name = [ x[0] for x in investigators ]
    last_name = [ x[1] for x in investigators ]
    organization = [ x[2] for x in investigators ]
    email = [ x[3] for x in investigators ]

    tmp = db.proposal.fields
    tmp.remove('id');
    tmp.remove('owner_');
    tmp.remove('investigators');
    tmp.remove('checklist');
    form = SQLFORM(db.proposal, _vars, fields=tmp)

    for option in db().select(db.checklist.name).as_list():
        name = option['name']
        if name in checklist:
            form[0].insert(-1, TR(TD(LABEL(name), _class='w2p_fl'), TD(INPUT(_name='checklist', _class='checkbox', _type='checkbox', _value=name, _checked='checked'), _class='w2p_fw')))
        else:
            form[0].insert(-1, TR(TD(LABEL(name), _class='w2p_fl'), TD(INPUT(_name='checklist', _class='checkbox', _type='checkbox', _value=name), _class='w2p_fw')))

    def get_or_default(l, index, *args):
        if index < len(l):
            return l[index]
        return args[0]

    for i in range(1, 6):
        form[0].insert(-1, TR(TD(H5('Investigator ' + str(i)), _class='w2p_fl')))
        form[0].insert(-1, TR(TD(LABEL('First Name'), _class='w2p_fl'), TD(INPUT(_name='first_name', _class='string', _type='text', _value=get_or_default(first_name, i-1, '')), _class='w2p_fw')))
        form[0].insert(-1, TR(TD(LABEL('Last Name'), _class='w2p_fl'), TD(INPUT(_name='last_name', _class='string', _type='text', _value=get_or_default(last_name, i-1, '')), _class='w2p_fw')))
        form[0].insert(-1, TR(TD(LABEL('Organization'), _class='w2p_fl'), TD(INPUT(_name='organization', _class='string', _type='text', _value=get_or_default(organization, i-1, '')), _class='w2p_fw')))
        form[0].insert(-1, TR(TD(LABEL('Email'), _class='w2p_fl'), TD(INPUT(_name='email', _class='string', _type='text', _value=get_or_default(email, i-1, '')), _class='w2p_fw')))

    return dict(form=form)
