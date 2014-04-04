# -*- coding: utf-8 -*-

import json
from gluon.storage import Storage

@auth.requires_login()
def index():
    grid = SQLFORM.grid(
        db.proposal.owner_ == auth.user.id,
        fields=[db.proposal.title, db.proposal.funding_agency, db.proposal.due_date],
        csv=False,
        details=False,
        searchable=False,
        custom_create_text='Create Proposal',
        custom_create_link=URL('update_proposal'),
        custom_edit_link=lambda row: URL('update_proposal', args=str(row['id'])),
    )
    return locals()

def user():
    form = auth()
    return locals()

@auth.requires_login()
def update_proposal():
    _id = None
    if len(request.args) > 0:
        try:
            _id = int(request.args[0])
        except: pass

    if _id != None:
        rows = db(db.proposal.id == _id).select(db.proposal.owner_)
        if len(rows) == 0 or rows[0]['owner_'] != auth.user.id:
            redirect(URL('index'))

    def get_list_from_field(a):
        if type(a) is list:
            return a
        return [a]

    if request.env.request_method == 'POST':
        _vars = request.vars
        ll = []
        for field in investigator_fields:
            ll.append([] if not field in _vars else get_list_from_field(_vars[field]))
        if _id == None:
            _vars.owner_ = auth.user.id
        _vars.investigators = json.dumps(zip(*ll))
        _vars.checklist = json.dumps(list(set(get_list_from_field(_vars.checklist))))
        _vars = { k : getattr(_vars, k) for k in _vars if k in db.proposal.fields and k != 'id' }
        if _id == None:
            db.proposal.insert(**_vars)
        else:
            db(db.proposal.id == _id).update(**_vars)
        redirect(URL('index'))

    _vars = dict()
    if _id != None:
        rows = db(db.proposal.id == _id).select(db.proposal.ALL)
        _vars = Storage(rows[0])
        _vars.investigators = json.loads(_vars.investigators)
        _vars.checklist = set(json.loads(_vars.checklist))

    tmp = db.proposal.fields[:]
    tmp.remove('owner_')
    tmp.remove('investigators')
    tmp.remove('checklist')
    form = SQLFORM(db.proposal, _vars, showid=False, fields=tmp)

    def get(l, index, default):
        if (type(l) is list and index < len(l)) or index in l:
            return l[index]
        return default

    if _id != None:
        checklist = get(_vars, 'checklist', [])
        for option in db().select(db.checklist.name):
            name = option['name']
            form[0].insert(-1, TR(TD(LABEL(name), _class='w2p_fl'), TD(INPUT(_name='checklist', _class='checkbox', _type='checkbox', _value=name, _checked='checked' if name in checklist else None), _class='w2p_fw')))

    investigators = get(_vars, 'investigators', [])
    for i in range(5):
        form[0].insert(-1, TR(TD(H5('Investigator ' + str(i+1)), _class='w2p_fl')))
        entry = get(investigators, i, [])
        for j in range(len(investigator_fields)):
            form[0].insert(-1, TR(TD(LABEL(investigator_fields[j]), _class='w2p_fl'), TD(INPUT(_name=investigator_fields[j], _class='string', _type='text', _value=get(entry, j, '')), _class='w2p_fw')))

    return dict(form=form)
