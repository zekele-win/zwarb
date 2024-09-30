#!/usr/bin/env python3
#-*-coding: utf-8-*-

import re
import random
import web3
from sdata_maker import *

def check_idx(var):
    if type(var) is str:
        r = re.match(r'^\{(\d+)\}$', var)
        if r:
            return int(r.group(1))
    return None

def calc_mps(idx_phs, types, values):
    mps = []
    w3 = web3.Web3()
    data = w3.codec.encode(types, values)
    for idx, ph in idx_phs:
        pos = data.index(ph.to_bytes(32, 'big'))
        mps.append((idx, 20+4+4+pos))
    return mps

def fake_values(idx_phs, values):
    is_tuple = type(values) is tuple
    if is_tuple:
        values = list(values)
    for i in range(len(values)):
        if type(values[i]) in (list, tuple):
            values[i] = fake_values(idx_phs, values[i])
        else:
            idx = check_idx(values[i])
            if idx is not None:
                ph = random.randint(2**251,2**252-1)
                idx_phs.append((idx, ph))
                values[i] = ph
    if is_tuple:
        values = tuple(values)
    return values

def unfake_values(idx_phs, values):
    phs = set()
    for idx, ph in idx_phs:
        phs.add(ph)
    is_tuple = type(values) is tuple
    if is_tuple:
        values = list(values)
    for i in range(len(values)):
        if type(values[i]) in (list, tuple):
            values[i] = unfake_values(idx_phs, values[i])
        else:
            if values[i] in phs:
                values[i] = 0
    if is_tuple:
        values = tuple(values)
    return values

def make(caddr, method, types, values, refs):
    types = [] if types is None else types
    values = [] if values is None else values

    idx_phs = []
    fake_values(idx_phs, values)
    map_params = calc_mps(idx_phs, types, values)
    values = unfake_values(idx_phs, values)

    ref_params = []
    if refs:
        pos = 0
        for idx in refs:
            if idx is not None:
                ref_params.append((idx, pos))
            pos += 32

    # print(f'map_params - {map_params}')
    # print(f'types - {types}')
    # print(f'values - {values}')
    # print(f'ref_params - {ref_params}')

    return make_sdata_handle(
        op = make_sdata_op_call,
        map_params = map_params,
        operator = (
            caddr, # caddr
            method, # method
            types, # types
            values, # values
        ),
        ref_params = ref_params,
    )

if __name__ == '__main__':
    from format_helper import format_hex

    assert make('0x5B38Da6a701c568545dCfcB03FcB875f56beddC4', 'invoke', ['uint256', 'uint256', 'uint256'], [0x1111, 0x2222, 0x3333], None).hex() == format_hex('''
        # op call
        00000000
        ## map_params
        # cnt
        00000000
        # caddr
        5b38da6a701c568545dcfcb03fcb875f56beddc4
        # elen
        00000064
        # edata
        e40ccc40000000000000000000000000000000000000000000000000000000000000111100000000000000000000000000000000000000000000000000000000000022220000000000000000000000000000000000000000000000000000000000003333
        ## ref_params
        # cnt
        00000000
    '''), "make('0x5B38Da6a701c568545dCfcB03FcB875f56beddC4', 'invoke', ['uint256', 'uint256', 'uint256'], [0x1111, 0x2222, 0x3333], None) fail"

    assert make('0x5B38Da6a701c568545dCfcB03FcB875f56beddC4', 'invoke', ['uint256', 'uint256', 'uint256'], ['{1}', '{2}', '{3}'], None).hex() == format_hex('''
        # op call
        00000000
        ## map_params
        # cnt
        00000003
        # idx[0]
        00000001
        # pos[0]
        0000001c
        # idx[1]
        00000002
        # pos[1]
        0000003c
        # idx[2]
        00000003
        # pos[2]
        0000005c
        # caddr
        5b38da6a701c568545dcfcb03fcb875f56beddc4
        # elen
        00000064
        # edata
        e40ccc40000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
        ## ref_params
        # cnt
        00000000
    '''), "make('0x5B38Da6a701c568545dCfcB03FcB875f56beddC4', 'invoke', ['uint256', 'uint256', 'uint256'], ['{1}', '{2}', '{3}'], None) fail"

    assert make('0x5B38Da6a701c568545dCfcB03FcB875f56beddC4', 'invoke', ['uint256', 'uint256', 'uint256'], ['{1}', '{2}', '{3}'], [1, None, 3]).hex() == format_hex('''
        # op call
        00000000
        ## map_params
        # cnt
        00000003
        # idx[0]
        00000001
        # pos[0]
        0000001c
        # idx[1]
        00000002
        # pos[1]
        0000003c
        # idx[2]
        00000003
        # pos[2]
        0000005c
        # caddr
        5b38da6a701c568545dcfcb03fcb875f56beddc4
        # elen
        00000064
        # edata
        e40ccc40000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
        ## ref_params
        # cnt
        00000002
        # idx[0]
        00000001
        # pos[0]
        00000000
        # idx[1]
        00000003
        # pos[1]
        00000040
    '''), "make('0x5B38Da6a701c568545dCfcB03FcB875f56beddC4', 'invoke', ['uint256', 'uint256', 'uint256'], ['{1}', '{2}', '{3}'], [1, None, 3]) fail"
