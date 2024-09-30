#!/usr/bin/env python3
#-*-coding: utf-8-*-

from sdata_maker import *

def make(addr, ref):
    return make_sdata_handle(
        op = make_sdata_op_balance,
        map_params = None,
        operator = (
            addr, # addr,
        ),
        ref_params = [(ref, 0)],
    )

if __name__ == '__main__':
    from format_helper import format_hex

    assert make('0x5B38Da6a701c568545dCfcB03FcB875f56beddC4', 1).hex() == format_hex('''
        # op balance
        00000002
        ## map_params
        # cnt
        00000000
        ## handle
        # addr
        5b38da6a701c568545dcfcb03fcb875f56beddc4
        ## ref_params
        # cnt
        00000001
        # idx[0]
        00000001
        # pos[0]
        00000000
    '''), "make('0x5B38Da6a701c568545dCfcB03FcB875f56beddC4', 1) fail"
