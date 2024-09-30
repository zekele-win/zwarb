#!/usr/bin/env python3
#-*-coding: utf-8-*-

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s [%(module)s] %(message)s')
logger = logging.getLogger()

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../maker'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../utils'))

from addrs import *
import sdata_maker
import sdata_maker_handle_call
import sdata_maker_handle_alg
import provider
import wallet
from tx_sender import *

class Inst:
    def __init__(self, w3, sender_addr, sender_pkey):
        self.w3 = w3
        self.sender_addr = sender_addr
        self.sender_pkey = sender_pkey

    def make(self, eth_amount):
        invoke = sdata_maker.make_sdata_invoke(
            build_params = None,
            handles = [
                sdata_maker_handle_alg.make(
                    exp = f'{eth_amount}',
                    ref = 0,
                ),
                sdata_maker_handle_call.make(
                    caddr = self.sender_addr,
                    method = None,
                    types = None,
                    values = None,
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

    def stat(self):
        amount = self.w3.eth.get_balance(self.sender_addr)
        logger.info(f'[stat] sender_addr eth balance - {amount}')
        amount = self.w3.eth.get_balance(arb_addr)
        logger.info(f'[stat] arb_addr eth balance - {amount}')

    def run(self, eth_amount):
        data = self.make(eth_amount)
        self.stat()
        self.execute(data)
        self.stat()

if __name__ == '__main__':
    # ganache --fork.url=<your provider endpoint> --fork.blockNumber=20000000 --wallet.accounts="0x741865f48be620eece5e191247e09c7e83d37c8461de63e9536caa1ce896e23a",1000000000000000000000 --wallet.accounts="0x08803d27e0408ba8db5c5ba2438a5ea39b5f5473f691916a014a3eb1719a8c22",1000000000000000000000

    eth_amount = int(float(sys.argv[1])*1e18)
    logger.info(f'eth_amount - {eth_amount}')

    w3 = provider.get_test_w3()
    sender_addr, sender_pkey = wallet.get_test()

    print('[prepare] for test')
    send_tx_data(w3 = w3,
        from_addr = sender_addr,
        to_addr = arb_addr,
        value = eth_amount,
        data = b'',
        gas = 1_000_000,
        priority_fee = int(0.1*1e9),
        max_fee = int(30.0*1e9),
        pkey = sender_pkey,
    )

    Inst(w3, sender_addr, sender_pkey).run(eth_amount)
