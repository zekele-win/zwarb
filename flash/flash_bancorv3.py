#!/usr/bin/env python3
#-*-coding: utf-8-*-

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../maker'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../abi'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../utils'))

from addrs import *
import sdata_maker_handle_call
import sdata_maker_handle_alg
import sdata_maker_handle_cond
from abi_loader import load_abi

class Inst:
    def __init__(self, w3, token_addr):
        self.w3 = w3
        self.token_addr = token_addr

    def calc_repay_amount(self, borrow_amount):
        bancorv3_settings = self.w3.eth.contract(address=bancorv3_settings_addr, abi=load_abi('bancor-v3/NetworkSettings'))
        flashLoanFeePPM = bancorv3_settings.functions.flashLoanFeePPM(self.token_addr).call()
        repay_amount = borrow_amount + borrow_amount * flashLoanFeePPM // 1_000_000
        return repay_amount

    def invoke(self, borrow_amount, callback_invoke):
        return [
            sdata_maker_handle_call.make(
                caddr = bancorv3_addr,
                method = 'flashLoan',
                types = [
                    'address', # Token token
                    'uint256', # uint256 amount
                    'address', # IFlashLoanRecipient recipient
                    'bytes', # bytes calldata data
                ],
                values = [
                    self.token_addr,
                    borrow_amount,
                    arb_addr,
                    callback_invoke,
                ],
                refs = None,
            ),
        ]

    def invoke_callback_build_params(self):
        return [
            (6, 32*2), # amount
            (7, 32*3), # feeAmount
        ]

    def invoke_callback_calc_repay(self):
        return [
            sdata_maker_handle_alg.make(
                exp = '{6}+{7}', # amount + feeAmount
                ref = 7, # repay_amount
            ),
        ]

    def invoke_callback_ret(self):
        return None

    def invoke_callback_repay(self, result_amount):
        handles = [
            sdata_maker_handle_cond.make(
                exp = f'{result_amount}>{{7}}', # result_amount > repay_amount
                msg = 'repay_amount unsufficient',
            ),
        ]

        if is_addr_native(self.token_addr):
            handles += [
                sdata_maker_handle_alg.make(
                    exp = '{7}',
                    ref = 0,
                ),
                sdata_maker_handle_call.make(
                    caddr = bancorv3_addr,
                    method = None,
                    types = None,
                    values = None,
                    refs = None,
                ),
            ]
        else:
            handles += [
                sdata_maker_handle_call.make(
                    caddr = self.token_addr,
                    method = 'transfer',
                    types = [
                        'address', # _to
                        'uint256', # _value
                    ],
                    values = [
                        bancorv3_addr,
                        '{7}', # repay_amount
                    ],
                    refs = None,
                ),
            ]

            handles += [
                sdata_maker_handle_alg.make(
                    exp = f'{result_amount}-{{7}}', # result_amount - repay_amount
                    ref = 7, # remain_amount
                ),
            ]

            if self.token_addr == weth_addr:
                handles += [
                    sdata_maker_handle_call.make(
                        caddr = weth_addr,
                        method = 'withdraw',
                        types = [
                            'uint256', # wad
                        ],
                        values = [
                            '{7}', # remain_amount
                        ],
                        refs = None,
                    ),
                ]
            else:
                handles += handles_input_approve(self.w3, uniswapv2_router02_addr, self.token_addr, '{7}') + [
                sdata_maker_handle_call.make(
                    caddr = uniswapv2_router02_addr,
                    method = 'swapExactTokensForETH',
                    types = [
                        'uint256', # uint amountIn,
                        'uint256', # uint amountOutMin,
                        'address[]', # address[] calldata path,
                        'address', # address to,
                        'uint256', # uint deadline
                    ],
                    values = [
                        '{7}',
                        0,
                        [
                            self.token_addr,
                            weth_addr,
                        ],
                        arb_addr,
                        2**256-1,
                    ],
                    refs = None,
                ),
            ]

        return handles

if __name__ == '__main__':
    import provider
    w3 = provider.get_test_w3()

    inst = Inst(w3 = w3, token_addr = eth_addr)
    print(inst.calc_repay_amount(int(1.0*1e18)))
    print(inst.invoke_callback_build_params())
    print(inst.invoke_callback_calc_repay())
    print(inst.invoke_callback_repay('{1}'))
