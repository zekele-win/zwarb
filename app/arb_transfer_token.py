#!/usr/bin/env python3
#-*-coding: utf-8-*-

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s [%(module)s] %(message)s')
logger = logging.getLogger()

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../maker'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../abi'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../utils'))

from addrs import *
import sdata_maker
import sdata_maker_handle_call
import sdata_maker_handle_alg
from abi_loader import load_abi
import provider
import wallet
from tx_sender import *

class Inst:
    def __init__(self, w3, sender_addr, sender_pkey):
        self.w3 = w3
        self.sender_addr = sender_addr
        self.sender_pkey = sender_pkey

    def make(self, token_addr, token_amount):
        invoke = sdata_maker.make_sdata_invoke(
            build_params = None,
            handles = [
                sdata_maker_handle_call.make(
                    caddr = token_addr,
                    method = 'transfer',
                    types = [
                        'address', # _to
                        'uint256', # _value
                    ],
                    values = [
                        self.sender_addr,
                        token_amount,
                    ],
                    refs = None,
                ),
            ],
            ret = None,
        )
        return sdata_maker.make_sdata(
            types = None,
            values = None,
            invoke = invoke,
        )

    def execute(self, data):
        send_tx_data(w3 = self.w3,
            from_addr = self.sender_addr,
            to_addr = arb_addr,
            value = 0,
            data = data,
            gas = 1_000_000,
            priority_fee = int(0.1*1e9),
            max_fee = int(30.0*1e9),
            pkey = self.sender_pkey,
        )

    def stat(self, token_addr):
        token = w3.eth.contract(address=token_addr, abi=load_abi('erc20/ERC20'))
        amount = token.functions.balanceOf(self.sender_addr).call()
        logger.info(f'[stat] sender_addr token balance - {amount}')
        amount = token.functions.balanceOf(arb_addr).call()
        logger.info(f'[stat] arb_addr token balance - {amount}')

    def run(self, token_addr, token_amount):
        data = self.make(token_addr, token_amount)
        self.stat(token_addr)
        self.execute(data)
        self.stat(token_addr)

if __name__ == '__main__':
    # ganache --fork.url=<your provider endpoint> --fork.blockNumber=20000000 --wallet.accounts="0x741865f48be620eece5e191247e09c7e83d37c8461de63e9536caa1ce896e23a",1000000000000000000000 --wallet.accounts="0x08803d27e0408ba8db5c5ba2438a5ea39b5f5473f691916a014a3eb1719a8c22",1000000000000000000000

    token_addr = sys.argv[1]
    token_amount = int(sys.argv[2])
    logger.info(f'token_addr - {token_addr}')
    logger.info(f'token_amount - {token_amount}')

    w3 = provider.get_test_w3()
    sender_addr, sender_pkey = wallet.get_test()

    print('[prepare] for test weth')
    weth = w3.eth.contract(address=weth_addr, abi=load_abi('erc20/WETH'))
    send_tx_contract(w3 = w3,
        from_addr = sender_addr,
        value = token_amount,
        contract = weth.functions.deposit(),
        gas = 1_000_000,
        priority_fee = int(0.1*1e9),
        max_fee = int(30.0*1e9),
        pkey = sender_pkey,
    )
    send_tx_contract(w3 = w3,
        from_addr = sender_addr,
        value = 0,
        contract = weth.functions.transfer(
            arb_addr,
            token_amount,
        ),
        gas = 1_000_000,
        priority_fee = int(0.1*1e9),
        max_fee = int(30.0*1e9),
        pkey = sender_pkey,
    )

    Inst(w3, sender_addr, sender_pkey).run(token_addr, token_amount)
