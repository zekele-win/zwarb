#!/usr/bin/env python3
#-*-coding: utf-8-*-

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../utils'))

from addrs import *

class SushiSwapV2Pair:
    def __init__(self, pair):
        self.pair = pair
        self.reserves = None

    def get_reserves(self):
        if self.reserves is None:
            self.reserves = self.pair.functions.getReserves().call()[:2]
        return self.reserves

    def swap(self, idx0, idx1, amountIn):
        reserves = self.get_reserves()
        return amountIn * 997 * reserves[idx1] // (reserves[idx0] * 1_000 + amountIn * 997)

class Inst:
    def __init__(self, pair, in_token, out_token):
        self.sushiSwapV2Pair = SushiSwapV2Pair(pair)
        self.in_token = in_token
        self.out_token = out_token

    def get_out_amount(self, in_amount):
        if in_amount <= 0:
            return 0
        (idx0, idx1) = (1, 0) if is_addr_pair_reverse(self.in_token, self.out_token) else (0, 1)
        return self.sushiSwapV2Pair.swap(idx0, idx1, in_amount)

if __name__ == '__main__':
    # ganache --fork.url=<your provider endpoint> --fork.blockNumber=20000000
    
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../abi'))

    from abi_loader import load_abi
    import provider

    w3 = provider.get_test_w3()
    uniswapv2_router02 = w3.eth.contract(address=uniswapv2_router02_addr, abi=load_abi('uniswap-v2/UniswapV2Router02'))
    uniswapv2_pair_usdc_eth = w3.eth.contract(address=uniswapv2_pair_usdc_eth_addr, abi=load_abi('uniswap-v2/UniswapV2Pair'))

    print(f'test from eth to usdc')
    conv_eth_amount = int(1.0 * 1e18)
    print(f'conv_eth_amount - {conv_eth_amount}')
    inst = Inst(uniswapv2_pair_usdc_eth, weth_addr, usdc_addr)
    conv_usdc_amount = inst.get_out_amount(conv_eth_amount)
    print(f'conv_usdc_amount - {conv_usdc_amount}')
    _, pool_usdc_amount = uniswapv2_router02.functions.getAmountsOut(
        amountIn = conv_eth_amount,
        path = [ weth_addr, usdc_addr ],
    ).call()
    print(f'pool_usdc_amount - {pool_usdc_amount}')
    assert conv_usdc_amount == pool_usdc_amount

    print(f'test from usdc to eth')
    conv_usdc_amount = int(3000 * 1e6)
    print(f'conv_usdc_amount - {conv_usdc_amount}')
    inst = Inst(uniswapv2_pair_usdc_eth, usdc_addr, weth_addr)
    conv_eth_amount = inst.get_out_amount(conv_usdc_amount)
    print(f'conv_eth_amount - {conv_eth_amount}')
    _, pool_eth_amount = uniswapv2_router02.functions.getAmountsOut(
        amountIn = conv_usdc_amount,
        path = [ usdc_addr, weth_addr ],
    ).call()
    print(f'pool_eth_amount - {pool_eth_amount}')
    assert conv_eth_amount == pool_eth_amount
