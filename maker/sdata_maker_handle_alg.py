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

def make(exp, ref):
    map_params = []
    svar = 0
    sop_tvars = []

    tag = 0
    pos = 0
    while True:
        if tag == 0:
            r = re.match('^([\{\}\d]+).*$', exp)
            var = r.group(1)
            idx = check_idx(var)
            if idx is not None:
                map_params.append((idx, pos))
                svar = 0
            else:
                svar = int(var)
            pos += 32+4
            tag = 1
        elif tag == 1:
            r = re.match('^(\+|\-|\*|\/).*$', exp)
            if not r:
                break
            sop = r.group(1)
            sop = ['+','-','*','/'].index(sop) + 1
            sop_tvars.append((sop, None))
            pos += 4
            tag = 2
        elif tag == 2:
            r = re.match('^([\{\}\d]+).*$', exp)
            var = r.group(1)
            idx = check_idx(var)
            if idx is not None:
                map_params.append((idx, pos))
                tvar = 0
            else:
                tvar = int(var)
            sop_tvars[-1] = (sop_tvars[-1][0], tvar)
            pos += 32
            tag = 1
        exp = exp[r.span(1)[-1]:]

    ref_params = [(ref, 0)]

    # print(f'map_params - {map_params}')
    # print(f'svar - {svar}')
    # print(f'sop_tvars - {sop_tvars}')
    # print(f'ref_params - {ref_params}')

    return make_sdata_handle(
        op = make_sdata_op_alg,
        map_params = map_params,
        operator = (
            svar, # svar,
            sop_tvars, # sop_tvars
        ),
        ref_params = ref_params,
    )

if __name__ == '__main__':
    from format_helper import format_hex

    assert make('55+44-33*22/11', 1).hex() == format_hex('''
        # op alg
        00000001
        ## map_params
        # cnt
        00000000
        ## handle
        # svar
        0000000000000000000000000000000000000000000000000000000000000037
        ## sop_tvars
        # cnt
        00000004
        # sop[0]
        00000001
        # tvar[0]
        000000000000000000000000000000000000000000000000000000000000002c
        # sop[1]
        00000002
        # tvar[1]
        0000000000000000000000000000000000000000000000000000000000000021
        # sop[2]
        00000003
        # tvar[2]
        0000000000000000000000000000000000000000000000000000000000000016
        # sop[3]
        00000004
        # tvar[3]
        000000000000000000000000000000000000000000000000000000000000000b
        ## ref_params
        # cnt
        00000001
        # idx[0]
        00000001
        # pos[0]
        00000000
    '''), "make('55+44-33*22/11', 1) fail"

    assert make('{1}+{2}-{3}*{4}/{5}', 1).hex() == format_hex('''
        # op alg
        00000001
        ## map_params
        # cnt
        00000005
        # idx[0]
        00000001
        # pos[0]
        00000000
        # idx[1]
        00000002
        # pos[1]
        00000028
        # idx[2]
        00000003
        # pos[2]
        0000004c
        # idx[3]
        00000004
        # pos[3]
        00000070
        # idx[4]
        00000005
        # pos[4]
        00000094
        ## handle
        # svar
        0000000000000000000000000000000000000000000000000000000000000000
        ## sop_tvars
        # cnt
        00000004
        # sop[0]
        00000001
        # tvar[0]
        0000000000000000000000000000000000000000000000000000000000000000
        # sop[1]
        00000002
        # tvar[1]
        0000000000000000000000000000000000000000000000000000000000000000
        # sop[2]
        00000003
        # tvar[2]
        0000000000000000000000000000000000000000000000000000000000000000
        # sop[3]
        00000004
        # tvar[3]
        0000000000000000000000000000000000000000000000000000000000000000
        ## ref_params
        # cnt
        00000001
        # idx[0]
        00000001
        # pos[0]
        00000000
    '''), "make('{1}+{2}-{3}*{4}/{5}', 1) fail"
