#!/usr/bin/env python3
#-*-coding: utf-8-*-

import logging
logger = logging.getLogger()

def send_tx(w3, tx, pkey, block_gap = 5):
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=pkey)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()
    logger.info(f'tx_hash - {tx_hash}')
    tx_res = w3.eth.wait_for_transaction_receipt(tx_hash)
    # logger.info(f'tx_res - {tx_res}')
    assert tx_res['status'] == 1, f'tx_res["status"] - {tx_res["status"]}'
    return tx_hash

def make_tx_data(w3, from_addr, to_addr, value, data, gas, priority_fee, max_fee):
    return {
        'from': from_addr,
        'to': to_addr,
        'value': value,
        'data': data,
        'nonce': w3.eth.get_transaction_count(from_addr),
        'chainId': w3.eth.chain_id,
        'gas': gas,
        'maxFeePerGas': max_fee,
        'maxPriorityFeePerGas': priority_fee,
        'type': 2,
    }

def send_tx_data(w3, from_addr, to_addr, value, data, gas, priority_fee, max_fee, pkey):
    return send_tx(w3, make_tx_data(w3, from_addr, to_addr, value, data, gas, priority_fee, max_fee), pkey)

def estimate_tx_data(w3, from_addr, to_addr, value, data, gas, priority_fee, max_fee):
    tx = make_tx_data(w3, from_addr, to_addr, value, data, gas, priority_fee, max_fee)
    return w3.eth.estimate_gas({'from':tx['from'], 'to':tx['to'], 'value':tx['value'], 'data':tx['data']})

def make_tx_contract(w3, from_addr, value, contract, gas, priority_fee, max_fee):
    return contract.build_transaction({
        'from': from_addr,
        'value': value,
        'nonce': w3.eth.get_transaction_count(from_addr),
        'chainId': w3.eth.chain_id,
        'gas': gas,
        'maxFeePerGas': max_fee,
        'maxPriorityFeePerGas': priority_fee,
        'type': 2,
    })

def send_tx_contract(w3, from_addr, value, contract, gas, priority_fee, max_fee, pkey):
    return send_tx(w3, make_tx_contract(w3, from_addr, value, contract, gas, priority_fee, max_fee), pkey)

def estimate_tx_contract(w3, from_addr, value, contract, gas, priority_fee, max_fee):
    tx = make_tx_contract(w3, from_addr, value, contract, gas, priority_fee, max_fee)
    return w3.eth.estimate_gas({'from':tx['from'], 'to':tx['to'], 'value':tx['value'], 'data':tx['data']})
