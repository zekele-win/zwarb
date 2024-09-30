#!/usr/bin/env python3
#-*-coding: utf-8-*-

from sdata_maker import *

def make(ref):
    return make_sdata_handle(
        op = make_sdata_op_gasprice,
        map_params = None,
        operator = None,
        ref_params = [(ref, 0)],
    )

if __name__ == '__main__':
    from format_helper import format_hex

    assert make(1).hex() == format_hex('''
        # op gasprice
        00000003
        ## map_params
        # cnt
        00000000
        ## handle
        ## ref_params
        # cnt
        00000001
        # idx[0]
        00000001
        # pos[0]
        00000000
    '''), "make(1) fail"
