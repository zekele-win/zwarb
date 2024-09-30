#!/usr/bin/env python3
#-*-coding: utf-8-*-

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../maker'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../conv'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../abi'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../utils'))

from abi_loader import load_abi
from addrs import *
import sdata_maker_handle_call
import conv_uniswapv2
from tran_helper import *

class Inst:
    def __init__(self, w3, input_token_addr, output_token_addr, pair_addr):
        self.w3 = w3
        self.input_token_addr = input_token_addr
        self.output_token_addr = output_token_addr
        self.pair_addr = pair_addr

    def invoke_transfer(self, input, output):
        if is_addr_native(self.input_token_addr):
            return self.invoke_transfer_eth_to_token(input, output)
        elif is_addr_native(self.output_token_addr):
            return self.invoke_transfer_token_to_eth(input, output)
        else:
            return self.invoke_transfer_token_to_token(input, output)

    def invoke_transfer_eth_to_token(self, input, output):
        return handles_input_approve(self.w3, uniswapv2_router02_addr, eth_addr, input) + [
            sdata_maker_handle_call.make(
                caddr = uniswapv2_router02_addr,
                method = 'swapExactETHForTokens',
                types = [
                    'uint256', # uint amountOutMin,
                    'address[]', # address[] calldata path,
                    'address', # address to,
                    'uint256', # uint deadline
                ],
                values = [
                    0,
                    [
                        weth_addr,
                        self.output_token_addr,
                    ],
                    arb_addr,
                    2**256-1,
                ],
                refs = [None, None, None, output] if output is not None else None,
            ),
        ]

    def invoke_transfer_token_to_eth(self, input, output):
        return handles_input_approve(self.w3, uniswapv2_router02_addr, self.input_token_addr, input) + [
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
                    input,
                    0,
                    [
                        self.input_token_addr,
                        weth_addr,
                    ],
                    arb_addr,
                    2**256-1,
                ],
                refs = [None, None, None, output] if output is not None else None,
            ),
        ]

    def invoke_transfer_token_to_token(self, input, output):
        return handles_input_approve(self.w3, uniswapv2_router02_addr, self.input_token_addr, input) + [
            sdata_maker_handle_call.make(
                caddr = uniswapv2_router02_addr,
                method = 'swapExactTokensForTokens',
                types = [
                    'uint256', # uint amountIn,
                    'uint256', # uint amountOutMin,
                    'address[]', # address[] calldata path,
                    'address', # address to,
                    'uint256', # uint deadline
                ],
                values = [
                    input,
                    0,
                    [
                        self.input_token_addr,
                        self.output_token_addr,
                    ],
                    arb_addr,
                    2**256-1,
                ],
                refs = [None, None, None, output] if output is not None else None,
            ),
        ]

    def make_conv(self):
        return conv_uniswapv2.Inst(
            pair = self.w3.eth.contract(address=self.pair_addr, abi=load_abi('uniswap-v2/UniswapV2Pair')),
            in_token = weth_addr if is_addr_native(self.input_token_addr) else self.input_token_addr,
            out_token = weth_addr if is_addr_native(self.output_token_addr) else self.output_token_addr,
        )

if __name__ == '__main__':
    # ganache --fork.url=<your provider endpoint> --fork.blockNumber=20000000 --wallet.accounts="0x741865f48be620eece5e191247e09c7e83d37c8461de63e9536caa1ce896e23a",1000000000000000000000 --wallet.accounts="0x08803d27e0408ba8db5c5ba2438a5ea39b5f5473f691916a014a3eb1719a8c22",1000000000000000000000

    import provider
    import wallet
    import sdata_maker
    from tx_sender import send_tx_data, send_tx_contract

    w3 = provider.get_test_w3()
    sender_addr, sender_pkey = wallet.get_test()

    weth = w3.eth.contract(address=weth_addr, abi=load_abi('erc20/WETH'))
    usdc = w3.eth.contract(address=usdc_addr, abi=load_abi('erc20/ERC20'))

    print('[prepare]')
    send_tx_data(w3 = w3,
        from_addr = sender_addr,
        to_addr = arb_addr,
        value = int(0.1*1e18),
        data = b'',
        gas = 1_000_000,
        priority_fee = int(0.1*1e9),
        max_fee = int(30.0*1e9),
        pkey = sender_pkey,
    )
    send_tx_data(w3 = w3,
        from_addr = sender_addr,
        to_addr = arb_addr,
        value = int(0.1*1e18),
        data = sdata_maker.make_sdata(
            types = None,
            values = None,
            invoke = sdata_maker.make_sdata_invoke(
                build_params = None,
                handles = [
                    sdata_maker_handle_alg.make(
                        exp = f'{int(0.1*1e18)}',
                        ref = 0,
                    ),
                    sdata_maker_handle_call.make(
                        caddr = weth_addr,
                        method = 'deposit',
                        types = None,
                        values = None,
                        refs = None,
                    ),
                ],
                ret = None,
            ),
        ),
        gas = 1_000_000,
        priority_fee = int(0.1*1e9),
        max_fee = int(30.0*1e9),
        pkey = sender_pkey,
    )
    amount = w3.eth.get_balance(arb_addr)
    print(f'arb_addr eth balance - {amount}')
    amount = weth.functions.balanceOf(arb_addr).call()
    print(f'arb_addr weth balance - {amount}')
    amount = usdc.functions.balanceOf(arb_addr).call()
    print(f'arb_addr usdc balance - {amount}')

    print('[test] from eth to usdc')
    input_eth_amount = int(0.01 * 1e18)
    inst = Inst(w3 = w3,
        input_token_addr = eth_addr,
        output_token_addr = usdc_addr,
        pair_addr = uniswapv2_pair_usdc_eth_addr,
    )
    conv_output_usdc_amount = inst.make_conv().get_out_amount(input_eth_amount)
    print(f'conv_output_usdc_amount - {conv_output_usdc_amount}')
    pre_usdc_amount = usdc.functions.balanceOf(arb_addr).call()
    send_tx_data(w3 = w3,
        from_addr = sender_addr,
        to_addr = arb_addr,
        value = 0,
        data = sdata_maker.make_sdata(
            types = None,
            values = None,
            invoke = sdata_maker.make_sdata_invoke(
                build_params = None,
                handles = inst.invoke_transfer(
                    input = input_eth_amount,
                    output = None,
                ),
                ret = None,
            ),
        ),
        gas = 1_000_000,
        priority_fee = int(0.1*1e9),
        max_fee = int(30.0*1e9),
        pkey = sender_pkey,
    )
    aft_usdc_amount = usdc.functions.balanceOf(arb_addr).call()
    arb_output_usdc_amount = aft_usdc_amount - pre_usdc_amount
    print(f'arb_output_usdc_amount - {arb_output_usdc_amount}')
    assert conv_output_usdc_amount == arb_output_usdc_amount

    print('[test] from usdc to eth')
    input_usdc_amount = int(10.0 * 1e6)
    inst = Inst(w3 = w3,
        input_token_addr = usdc_addr,
        output_token_addr = eth_addr,
        pair_addr = uniswapv2_pair_usdc_eth_addr,
    )
    conv_output_eth_amount = inst.make_conv().get_out_amount(input_usdc_amount)
    print(f'conv_output_eth_amount - {conv_output_eth_amount}')
    pre_eth_amount = w3.eth.get_balance(arb_addr)
    send_tx_data(w3 = w3,
        from_addr = sender_addr,
        to_addr = arb_addr,
        value = 0,
        data = sdata_maker.make_sdata(
            types = None,
            values = None,
            invoke = sdata_maker.make_sdata_invoke(
                build_params = None,
                handles = inst.invoke_transfer(
                    input = input_usdc_amount,
                    output = None,
                ),
                ret = None,
            ),
        ),
        gas = 1_000_000,
        priority_fee = int(0.1*1e9),
        max_fee = int(30.0*1e9),
        pkey = sender_pkey,
    )
    aft_eth_amount = w3.eth.get_balance(arb_addr)
    arb_output_eth_amount = aft_eth_amount - pre_eth_amount
    print(f'arb_output_eth_amount - {arb_output_eth_amount}')
    assert conv_output_eth_amount == arb_output_eth_amount

    print('[test] from weth to usdc')
    input_weth_amount = int(0.1 * 1e18)
    inst = Inst(w3 = w3,
        input_token_addr = weth_addr,
        output_token_addr = usdc_addr,
        pair_addr = uniswapv2_pair_usdc_eth_addr,
    )
    conv_output_usdc_amount = inst.make_conv().get_out_amount(input_weth_amount)
    print(f'conv_output_usdc_amount - {conv_output_usdc_amount}')
    pre_usdc_amount = usdc.functions.balanceOf(arb_addr).call()
    send_tx_data(w3 = w3,
        from_addr = sender_addr,
        to_addr = arb_addr,
        value = 0,
        data = sdata_maker.make_sdata(
            types = None,
            values = None,
            invoke = sdata_maker.make_sdata_invoke(
                build_params = None,
                handles = inst.invoke_transfer(
                    input = input_weth_amount,
                    output = None,
                ),
                ret = None,
            ),
        ),
        gas = 1_000_000,
        priority_fee = int(0.1*1e9),
        max_fee = int(30.0*1e9),
        pkey = sender_pkey,
    )
    aft_usdc_amount = usdc.functions.balanceOf(arb_addr).call()
    arb_output_usdc_amount = aft_usdc_amount - pre_usdc_amount
    print(f'arb_output_usdc_amount - {arb_output_usdc_amount}')
    assert conv_output_usdc_amount == arb_output_usdc_amount
