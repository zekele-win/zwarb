#!/usr/bin/env python3
#-*-coding: utf-8-*-

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../maker'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../abi'))

from abi_loader import load_abi
from addrs import *
import sdata_maker_handle_call
import sdata_maker_handle_alg

def handles_input_approve(w3, contract_addr, token_addr, input):
    if is_addr_native(token_addr):
        return [sdata_maker_handle_alg.make(
            exp = f'{input}',
            ref = 0,
        )]
    else:
        token = w3.eth.contract(address=token_addr, abi=load_abi('erc20/ERC20'))
        approve_token_to_contract = token.functions.allowance(_owner=arb_addr, _spender=contract_addr).call() == 0
        if approve_token_to_contract:
            return [sdata_maker_handle_call.make(
                caddr = token_addr,
                method = 'approve',
                types = [
                    'address',
                    'uint256',
                ],
                values = [
                    contract_addr,
                    (2**256-1),
                ],
                refs = None,
            )]
    return []
