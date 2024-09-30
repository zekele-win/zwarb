#!/usr/bin/env python3
#-*-coding: utf-8-*-


import web3

def get_w3():
    provider_endpoint = '<your provider endpoint>'
    w3 = web3.Web3(web3.Web3.HTTPProvider(provider_endpoint))
    w3.middleware_onion.add(web3.middleware.simple_cache_middleware)
    return w3

def get_test_w3():
    provider_endpoint = 'http://127.0.0.1:8545'
    w3 = web3.Web3(web3.Web3.HTTPProvider(provider_endpoint))
    w3.middleware_onion.add(web3.middleware.simple_cache_middleware)
    return w3
