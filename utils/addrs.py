#!/usr/bin/env python3
#-*-coding: utf-8-*-

arb_addr = '<your deployed arb addr>'
# TEST
arb_addr = '0x79554D67023eCDa6Ba2D73a2C0859494a376B464'

empty_addr = '0x0000000000000000000000000000000000000000'
eth_addr = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'

weth_addr = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
usdc_addr = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'

uniswapv2_router02_addr = '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
uniswapv2_pair_usdc_eth_addr = '0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc'

sushiswapv2_router02_addr = '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F'
sushiswapv2_pair_usdc_eth_addr = '0x397FF1542f962076d0BFE58eA045FfA2d347ACa0'

bancorv3_addr = '0xeEF417e1D5CC832e619ae18D2F140De2999dD4fB'
bancorv3_settings_addr = '0x83E1814ba31F7ea95D216204BB45FE75Ce09b14F'

def is_addr_native(addr):
    return addr in [empty_addr, eth_addr]

def is_addr_pair_reverse(addr0, addr1):
    return addr0.lower() > addr1.lower()
