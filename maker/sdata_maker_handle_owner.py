#!/usr/bin/env python3
#-*-coding: utf-8-*-

from sdata_maker import *

def make(addr):
    return make_sdata_handle(
        op = make_sdata_op_owner,
        map_params = None,
        operator = (
            addr, # addr,
        ),
        ref_params = None,
    )

if __name__ == '__main__':
    from format_helper import format_hex

    assert make('0x5B38Da6a701c568545dCfcB03FcB875f56beddC4').hex() == format_hex('''
        # op balance
        000000ff
        ## map_params
        # cnt
        00000000
        ## handle
        # addr
        5b38da6a701c568545dcfcb03fcb875f56beddc4
        ## ref_params
        00000000
    '''), "make('0x5B38Da6a701c568545dCfcB03FcB875f56beddC4') fail"
