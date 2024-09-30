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
import sdata_maker_handle_owner
import provider
import wallet
from tx_sender import *

class Inst:
    def __init__(self, w3, sender_addr, sender_pkey):
        self.w3 = w3
        self.sender_addr = sender_addr
        self.sender_pkey = sender_pkey

    def make(self, new_owner_addr):
        invoke = sdata_maker.make_sdata_invoke(
            build_params = None,
            handles = [
                sdata_maker_handle_owner.make(
                    addr = new_owner_addr,
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

    def run(self, new_owner_addr):
        data = self.make(new_owner_addr)
        self.execute(data)

if __name__ == '__main__':
    # ganache --fork.url=<your provider endpoint> --fork.blockNumber=20000000 --wallet.accounts="0x741865f48be620eece5e191247e09c7e83d37c8461de63e9536caa1ce896e23a",1000000000000000000000 --wallet.accounts="0x08803d27e0408ba8db5c5ba2438a5ea39b5f5473f691916a014a3eb1719a8c22",1000000000000000000000

    new_owner_addr = sys.argv[1]
    logger.info(f'new_owner_addr - {new_owner_addr}')

    w3 = provider.get_test_w3()
    sender_addr, sender_pkey = wallet.get_test()

    Inst(w3, sender_addr, sender_pkey).run(new_owner_addr)
