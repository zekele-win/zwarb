#!/usr/bin/env python3
#-*-coding: utf-8-*-

import os

def load_abi(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{name}.json')
    with open(path) as f:
        return f.read()
