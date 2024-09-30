#!/usr/bin/env python3
#-*-coding: utf-8-*-

import re
from sdata_maker import *

def check_idx(var):
    if type(var) is str:
        r = re.match(r'^\{(\d+)\}$', var)
        if r:
            return int(r.group(1))
    return None

def make(exp, msg):
    r = re.match(r'^([\{\}\d]+)(==|\<|\<=|\>|\>=)([\{\}\d]+)$', exp)
    svar = r.group(1)
    sop = r.group(2)
    tvar = r.group(3)

    map_params = []

    sop = ['==','<','<=','>','>='].index(sop) + 1

    idx = check_idx(svar)
    if idx is not None:
        map_params.append((idx, 0))
        svar = 0
    else:
        svar = int(svar)

    idx = check_idx(tvar)
    if idx is not None:
        map_params.append((idx, 32+4))
        tvar = 0
    else:
        tvar = int(tvar)

    # print(f'map_params - {map_params}')
    # print(f'sop - {sop}')
    # print(f'svar - {svar}')
    # print(f'tvar - {tvar}')

    return make_sdata_handle(
        op = make_sdata_op_cond,
        map_params = map_params,
        operator = (
            svar, # svar
            sop, # sop
            tvar, # tvar
            msg, # msg
        ),
        ref_params = None,
    )

if __name__ == '__main__':
    from format_helper import format_hex

    assert make('1234==1234', 'abcd').hex() == format_hex('''
        # op cond
        00000010
        ## map_params
        # cnt
        00000000
        ## handle
        # svar
        00000000000000000000000000000000000000000000000000000000000004d2
        # sop equal
        00000001
        # tvar
        00000000000000000000000000000000000000000000000000000000000004d2
        ## emsg
        # len
        00000004
        # data
        61626364
        ## ref_params
        # cnt
        00000000
    '''), "make('1234==1234', 'abcd') fail"

    assert make('1234<5678', 'abcd').hex() == format_hex('''
        # op cond
        00000010
        ## map_params
        # cnt
        00000000
        ## handle
        # svar
        00000000000000000000000000000000000000000000000000000000000004d2
        # sop below
        00000002
        # tvar
        000000000000000000000000000000000000000000000000000000000000162e
        ## emsg
        # len
        00000004
        # data
        61626364
        ## ref_params
        # cnt
        00000000
    '''), "make('1234<5678', 'abcd') fail"

    assert make('1234<=5678', 'abcd').hex() == format_hex('''
        # op cond
        00000010
        ## map_params
        # cnt
        00000000
        ## handle
        # svar
        00000000000000000000000000000000000000000000000000000000000004d2
        # sop below or equal
        00000003
        # tvar
        000000000000000000000000000000000000000000000000000000000000162e
        ## emsg
        # len
        00000004
        # data
        61626364
        ## ref_params
        # cnt
        00000000
    '''), "make('1234<=5678', 'abcd') fail"

    assert make('5678>1234', 'abcd').hex() == format_hex('''
        # op cond
        00000010
        ## map_params
        # cnt
        00000000
        ## handle
        # svar
        000000000000000000000000000000000000000000000000000000000000162e
        # sop greater
        00000004
        # tvar
        00000000000000000000000000000000000000000000000000000000000004d2
        ## emsg
        # len
        00000004
        # data
        61626364
        ## ref_params
        # cnt
        00000000
    '''), "make('5678>1234', 'abcd') fail"

    assert make('5678>=1234', 'abcd').hex() == format_hex('''
        # op cond
        00000010
        ## map_params
        # cnt
        00000000
        ## handle
        # svar
        000000000000000000000000000000000000000000000000000000000000162e
        # sop greater or equal
        00000005
        # tvar
        00000000000000000000000000000000000000000000000000000000000004d2
        ## emsg
        # len
        00000004
        # data
        61626364
        ## ref_params
        # cnt
        00000000
    '''), "make('5678>=1234', 'abcd') fail"

    assert make('{1}=={2}', 'abcd').hex() == format_hex('''
        # op cond
        00000010
        ## map_params
        # cnt
        00000002
        # idx[0]
        00000001
        # pos[0]
        00000000
        # idx[1]
        00000002
        # pos[1]
        00000024
        ## handle
        # svar
        0000000000000000000000000000000000000000000000000000000000000000
        # sop equal
        00000001
        # tvar
        0000000000000000000000000000000000000000000000000000000000000000
        ## emsg
        # len
        00000004
        # data
        61626364
        ## ref_params
        # cnt
        00000000
    '''), "make('{1}=={2}', 'abcd') fail"

    assert make('{1}<{2}', 'abcd').hex() == format_hex('''
        # op cond
        00000010
        ## map_params
        # cnt
        00000002
        # idx[0]
        00000001
        # pos[0]
        00000000
        # idx[1]
        00000002
        # pos[1]
        00000024
        ## handle
        # svar
        0000000000000000000000000000000000000000000000000000000000000000
        # sop below
        00000002
        # tvar
        0000000000000000000000000000000000000000000000000000000000000000
        ## emsg
        # len
        00000004
        # data
        61626364
        ## ref_params
        # cnt
        00000000
    '''), "make('{1}<{2}', 'abcd') fail"

    assert make('{1}<={2}', 'abcd').hex() == format_hex('''
        # op cond
        00000010
        ## map_params
        # cnt
        00000002
        # idx[0]
        00000001
        # pos[0]
        00000000
        # idx[1]
        00000002
        # pos[1]
        00000024
        ## handle
        # svar
        0000000000000000000000000000000000000000000000000000000000000000
        # sop below or equal
        00000003
        # tvar
        0000000000000000000000000000000000000000000000000000000000000000
        ## emsg
        # len
        00000004
        # data
        61626364
        ## ref_params
        # cnt
        00000000
    '''), "make('{1}<={2}', 'abcd') fail"

    assert make('{1}>{2}', 'abcd').hex() == format_hex('''
        # op cond
        00000010
        ## map_params
        # cnt
        00000002
        # idx[0]
        00000001
        # pos[0]
        00000000
        # idx[1]
        00000002
        # pos[1]
        00000024
        ## handle
        # svar
        0000000000000000000000000000000000000000000000000000000000000000
        # sop greater
        00000004
        # tvar
        0000000000000000000000000000000000000000000000000000000000000000
        ## emsg
        # len
        00000004
        # data
        61626364
        ## ref_params
        # cnt
        00000000
    '''), "make('{1}>{2}', 'abcd') fail"

    assert make('{1}>={2}', 'abcd').hex() == format_hex('''
        # op cond
        00000010
        ## map_params
        # cnt
        00000002
        # idx[0]
        00000001
        # pos[0]
        00000000
        # idx[1]
        00000002
        # pos[1]
        00000024
        ## handle
        # svar
        0000000000000000000000000000000000000000000000000000000000000000
        # sop greater or equal
        00000005
        # tvar
        0000000000000000000000000000000000000000000000000000000000000000
        ## emsg
        # len
        00000004
        # data
        61626364
        ## ref_params
        # cnt
        00000000
    '''), "make('{1}>={2}', 'abcd') fail"
