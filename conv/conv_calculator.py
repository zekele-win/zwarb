#!/usr/bin/env python3
#-*-coding: utf-8-*-

def calc_diff(convs, amount0):
    amount = amount0
    for conv in convs:
        amount = conv.get_out_amount(in_amount = amount)
    return amount - amount0

def calc_amount(convs, low_amount, high_amount):
    middle_amount = (high_amount - low_amount) // 2 + low_amount
    low_middle_amount = (middle_amount - low_amount) // 2 + low_amount
    high_middle_amount = (high_amount - middle_amount) // 2 + middle_amount

    low_middle_diff = calc_diff(convs, low_middle_amount)
    high_middle_diff = calc_diff(convs, high_middle_amount)

    # print(f'low_amount, high_amount, low_middle_diff, high_middle_diff - {low_amount}, {high_amount}, {low_middle_diff}, {high_middle_diff}')
    # print(f'min_amount, max_diff - {min(low_amount, high_amount)}, {max(low_middle_diff, high_middle_diff)}')

    if low_middle_diff < high_middle_diff:
        return middle_amount, high_amount
    else:
        return low_amount, middle_amount

def calc(convs, low_amount, high_amount):
    amount0 = 0
    # print(f'low_amount, high_amount - {low_amount}, {high_amount}')
    while True:
        low_amount, high_amount = calc_amount(convs, low_amount, high_amount)
        # print(f'low_amount, high_amount - {low_amount}, {high_amount}')
        if low_amount == high_amount or low_amount + 1 == high_amount:
            amount0 = low_amount
            break

    diff = calc_diff(convs, amount0)
    amounts = [amount0]
    for conv in convs:
        amounts.append(conv.get_out_amount(in_amount = amounts[-1]))

    return diff, amounts

if __name__ == '__main__':
    import os, sys
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../abi'))
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../utils'))

    from abi_loader import load_abi
    from addrs import *
    import provider

    import conv_uniswapv2
    import conv_sushiswapv2

    w3 = provider.get_test_w3()
    uniswapv2_pair_usdc_eth = w3.eth.contract(address=uniswapv2_pair_usdc_eth_addr, abi=load_abi('uniswap-v2/UniswapV2Pair'))
    sushiswapv2_pair_usdc_eth = w3.eth.contract(address=sushiswapv2_pair_usdc_eth_addr, abi=load_abi('sushiswap-v2/SushiSwapV2Pair'))

    diff, amounts = calc([
        conv_uniswapv2.Inst(
            pair = uniswapv2_pair_usdc_eth,
            in_token = weth_addr,
            out_token = usdc_addr,
        ),
        conv_sushiswapv2.Inst(
            pair = sushiswapv2_pair_usdc_eth,
            in_token = usdc_addr,
            out_token = weth_addr,
        ),
    ], int(0.001*1e18), int(100*1e18))
    print(f'calc - {diff} {amounts}')

    diff, amounts = calc([
        conv_sushiswapv2.Inst(
            pair = sushiswapv2_pair_usdc_eth,
            in_token = weth_addr,
            out_token = usdc_addr,
        ),
        conv_uniswapv2.Inst(
            pair = uniswapv2_pair_usdc_eth,
            in_token = usdc_addr,
            out_token = weth_addr,
        ),
    ], int(0.001*1e18), int(100*1e18))
    print(f'calc - {diff} {amounts}')
