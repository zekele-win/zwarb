#!/usr/bin/env python3
#-*-coding: utf-8-*-

import logging
logger = logging.getLogger()

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../maker'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../conv'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../tran'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../flash'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../abi'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../utils'))

from addrs import *
import sdata_maker
import sdata_maker_handle_call
import sdata_maker_handle_alg
import sdata_maker_handle_cond
import sdata_maker_handle_balance
from abi_loader import load_abi
import provider
import wallet
import conv_calculator
from tx_sender import *

class Inst:
    def __init__(self, w3, sender_addr, sender_pkey, flash, trans, conv_low_amount = int(0.001*1e18), conv_high_amount = int(100.0*1e18)):
        self.w3 = w3
        self.sender_addr = sender_addr
        self.sender_pkey = sender_pkey
        self.flash = flash
        self.trans = trans
        self.conv_low_amount = conv_low_amount
        self.conv_high_amount = conv_high_amount

    def make(self, borrow_amount):
        tran_handles = []
        input, output = borrow_amount, 1
        for tran in self.trans:
            tran_handles += tran.invoke_transfer(input, output)
            input, output = '{1}', 1

        callback_invoke = sdata_maker.make_sdata_invoke(
            build_params = self.flash.invoke_callback_build_params(),
            handles = self.flash.invoke_callback_calc_repay() +
                tran_handles +
                self.flash.invoke_callback_repay('{1}'),
            ret = self.flash.invoke_callback_ret(),
        )

        invoke = sdata_maker.make_sdata_invoke(
            build_params = None,
            handles = [
                self.flash.invoke(borrow_amount, callback_invoke),
            ] + self.handles_return_eth(),
            ret = None,
        )

        return sdata_maker.make_sdata(
            types = None,
            values = None,
            invoke = invoke,
        )

    def handles_return_eth(self):
        return [
            # get eth_remain_amount
            sdata_maker_handle_balance.make(
                addr = arb_addr,
                ref = 1, # eth_remain_amount
            ),

            # transfer eth_remain_amount
            sdata_maker_handle_alg.make(
                exp = '{1}', # eth_remain_amount
                ref = 0, # eth_remain_amount
            ),
            sdata_maker_handle_call.make(
                caddr = self.sender_addr,
                method = None,
                types = None,
                values = None,
                refs = None,
            ),
        ]

    def calculate(self):
        convs = [tran.make_conv() for tran in self.trans]

        diff, amounts = conv_calculator.calc(convs, self.conv_low_amount, self.conv_high_amount)
        logger.info(f'[calculate] conv_calculator - {diff} - {amounts}')
        assert diff > 0, f'conv_calculator fail'
        borrow_amount, result_amount = amounts[0], amounts[-1]

        repay_amount = self.flash.calc_repay_amount(borrow_amount)
        logger.info(f'[calculate] repay_amount - {repay_amount}')
        assert result_amount > repay_amount, f'result_amount unsufficient'
        remain_amount = result_amount - repay_amount
        logger.info(f'[calculate] remain_amount - {remain_amount}')

        return borrow_amount, remain_amount

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

    def run(self):
        borrow_amount, remain_amount = self.calculate()
        data = self.make(borrow_amount)
        self.execute(data)
