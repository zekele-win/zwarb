#!/usr/bin/env python3
#-*-coding: utf-8-*-

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s [%(module)s] %(message)s')
logger = logging.getLogger()

def stat(w3, sender_addr, arb_addr):
    amount = w3.eth.get_balance(sender_addr)
    logger.info(f'[stat] sender_addr eth balance - {amount}')
    amount = w3.eth.get_balance(arb_addr)
    logger.info(f'[stat] arb_addr eth balance - {amount}')

if __name__ == '__main__':
    # ganache --fork.url=<your provider endpoint> --fork.blockNumber=20000000 --wallet.accounts="0x741865f48be620eece5e191247e09c7e83d37c8461de63e9536caa1ce896e23a",1000000000000000000000 --wallet.accounts="0x08803d27e0408ba8db5c5ba2438a5ea39b5f5473f691916a014a3eb1719a8c22",1000000000000000000000

    import os, sys
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../abi'))
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../tran'))
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../flash'))
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../utils'))

    from addrs import *
    from abi_loader import load_abi
    from tx_sender import send_tx_contract
    import provider
    import wallet
    import flash_bancorv3
    import tran_uniswapv2
    import tran_sushiswapv2
    import app_trans

    w3 = provider.get_test_w3()
    sender_addr, sender_pkey = wallet.get_test()

    usdc = w3.eth.contract(address=usdc_addr, abi=load_abi('erc20/ERC20'))
    uniswapv2_router02 = w3.eth.contract(address=uniswapv2_router02_addr, abi=load_abi('uniswap-v2/UniswapV2Router02'))
    sushiswapv2_router02 = w3.eth.contract(address=sushiswapv2_router02_addr, abi=load_abi('sushiswap-v2/SushiSwapV2Router02'))

    print('[prepare] for test')
    # send eth to sushiswapv2
    eth_amount = int(100*1e18)
    send_tx_contract(w3 = w3,
        from_addr = sender_addr,
        value = eth_amount,
        contract = sushiswapv2_router02.functions.swapExactETHForTokens(
            amountOutMin = 0,
            path = [ weth_addr, usdc_addr ],
            to = sender_addr,
            deadline = 2**256-1,
        ),
        gas = 1_000_000,
        priority_fee = int(0.1*1e9),
        max_fee = int(30.0*1e9),
        pkey = sender_pkey,
    )
    usdc_amount = usdc.functions.balanceOf(sender_addr).call()
    print(f'[test] usdc_amount - {usdc_amount}')
    # send usdc to uniswapv2
    send_tx_contract(w3 = w3,
        from_addr = sender_addr,
        value = 0,
        contract = usdc.functions.approve(
            uniswapv2_router02_addr,
            (2**256-1),
        ),
        gas = 1_000_000,
        priority_fee = int(0.1*1e9),
        max_fee = int(30.0*1e9),
        pkey = sender_pkey,
    )
    send_tx_contract(w3 = w3,
        from_addr = sender_addr,
        value = 0,
        contract = uniswapv2_router02.functions.swapExactTokensForETH(
            amountIn = usdc_amount,
            amountOutMin = 0,
            path = [ usdc_addr, weth_addr ],
            to = sender_addr,
            deadline = 2**256-1,
        ),
        gas = 1_000_000,
        priority_fee = int(0.1*1e9),
        max_fee = int(30.0*1e9),
        pkey = sender_pkey,
    )

    stat(w3, sender_addr, arb_addr)
    app_trans.Inst(
        w3 = w3,
        sender_addr = sender_addr,
        sender_pkey= sender_pkey,
        flash = flash_bancorv3.Inst(w3 = w3, token_addr = eth_addr),
        trans = [
            tran_uniswapv2.Inst(w3 = w3,
                input_token_addr = eth_addr,
                output_token_addr = usdc_addr,
                pair_addr = uniswapv2_pair_usdc_eth_addr,
            ),
            tran_sushiswapv2.Inst(w3 = w3,
                input_token_addr = usdc_addr,
                output_token_addr = eth_addr,
                pair_addr = sushiswapv2_pair_usdc_eth_addr,
            ),
        ],
    ).run()
    stat(w3, sender_addr, arb_addr)
