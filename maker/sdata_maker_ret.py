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

def make(rets):
    map_params = []
    rdata = b''
    if not rets:
        rets = []
    if type(rets) is not list:
        rets = [rets]
    pos = 4 # rlen place holder
    for ret in rets:
        idx = check_idx(ret)
        if idx is not None:
            map_params.append((idx, pos))
            rdata += int(0).to_bytes(32, 'big')
        else:
            rdata += ret.to_bytes(32, 'big')
        pos += 32 # uint256 per rdata place holder

    # print(f'map_params - {map_params}')
    # print(f'rdata - {rdata}')

    return make_sdata_ret(map_params, rdata)

if __name__ == '__main__':
    from format_helper import format_hex

    assert make(None).hex() == format_hex('''
        ## map_params
        # cnt
        00000000
        ## ret
        # len
        00000000
    '''), 'make(None) fail'

    assert make(1).hex() == format_hex('''
        ## map_params
        # cnt
        00000000
        ## ret
        # len
        00000020
        # data[0]
        0000000000000000000000000000000000000000000000000000000000000001
    '''), 'make(1) fail'

    assert make('{1}').hex() == format_hex('''
        ## map_params
        # cnt
        00000001
        # idx[0]
        00000001
        # pos[0]
        00000004
        ## ret
        # len
        00000020
        # data[0]
        0000000000000000000000000000000000000000000000000000000000000000
    '''), 'make({1}) fail'

    assert make([1,2]).hex() == format_hex('''
        ## map_params
        # cnt
        00000000
        ## ret
        # len
        00000040
        # data[0]
        0000000000000000000000000000000000000000000000000000000000000001
        # data[1]
        0000000000000000000000000000000000000000000000000000000000000002
    '''), 'make([1,2]) fail'

    assert make(['{1}','{2}']).hex() == format_hex('''
        ## map_params
        # cnt
        00000002
        # idx[0]
        00000001
        # pos[0]
        00000004
        # idx[1]
        00000002
        # pos[2]
        00000024
        ## ret
        # len
        00000040
        # data[0]
        0000000000000000000000000000000000000000000000000000000000000000
        # data[1]
        0000000000000000000000000000000000000000000000000000000000000000
    '''), 'make([{1},{2}]) fail'
