#!/usr/bin/env python3
#-*-coding: utf-8-*-

def format_hex(h):
    nh = ''
    cs = h.split('\n')
    for c in cs:
        c = c.strip()
        i = c.find('#')
        if i >= 0:
            c = c[:i].strip()
        if not c:
            continue
        nh += c
    return nh
