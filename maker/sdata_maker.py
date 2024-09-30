#!/usr/bin/env python3
#-*-coding: utf-8-*-

import web3

make_sdata_holder_tag = 0xdc32c08af781414c33b1d3b42fb497679827654685f8ee3388e4623d21467dc3
make_sdata_addr_coinbase = '0x0000000000000000000000000000000000000000'

make_sdata_op_call = 0x00
make_sdata_op_alg = 0x01
make_sdata_op_balance = 0x02
make_sdata_op_gasprice = 0x03
make_sdata_op_gasleft = 0x04
make_sdata_op_cond = 0x10
make_sdata_op_owner = 0xff

make_sdata_op_alg_sop_add = 0x01
make_sdata_op_alg_sop_sub = 0x02
make_sdata_op_alg_sop_mul = 0x03
make_sdata_op_alg_sop_div = 0x04

make_sdata_op_cond_sop_equal = 0x01
make_sdata_op_alg_sop_below = 0x02
make_sdata_op_alg_sop_below_equal = 0x03
make_sdata_op_cond_sop_above = 0x04
make_sdata_op_alg_sop_above_equal = 0x05

def make_sdata_holder():
    return make_sdata_holder_tag.to_bytes(32, 'big')

def make_sdata_params(idx_poss):
    idx_poss = idx_poss if idx_poss else []
    d = len(idx_poss).to_bytes(4, 'big')
    for idx, pos in idx_poss:
        d += idx.to_bytes(4, 'big')
        d += pos.to_bytes(4, 'big')
    return d

def make_sdata_handle_call(caddr, method, types, values):
    types = types if types else []
    values = values if values else []
    d = bytes.fromhex(caddr[2:])
    if method:
        w3 = web3.Web3()
        if method.startswith('0x'):
            sig = bytes.fromhex(method[2:])
        else:
            sig = w3.keccak(text=f'{method}({",".join(types)})')[:4]
        edata = sig + w3.codec.encode(types, values)
    else:
        edata = b''
    d += len(edata).to_bytes(4, 'big') + edata
    return d

def make_sdata_handle_alg(svar, sop_tvars):
    d = svar.to_bytes(32, 'big')
    sop_tvars = sop_tvars if sop_tvars else []
    d += len(sop_tvars).to_bytes(4, 'big')
    for sop, tvar in sop_tvars:
        d += sop.to_bytes(4, 'big')
        d += tvar.to_bytes(32, 'big')
    return d

def make_sdata_handle_balance(addr):
    return bytes.fromhex(addr[2:])

def make_sdata_handle_gasprice():
    return b''

def make_sdata_handle_gasleft():
    return b''

def make_sdata_handle_cond(svar, sop, tvar, msg):
    d = svar.to_bytes(32, 'big')
    d += sop.to_bytes(4, 'big')
    d += tvar.to_bytes(32, 'big')
    emsg = msg.encode('utf8')
    d += len(emsg).to_bytes(4, 'big') + emsg
    return d

def make_sdata_handle_owner(addr):
    return bytes.fromhex(addr[2:])

def make_sdata_handle(op, map_params, operator, ref_params):
    d = op.to_bytes(4, 'big')
    d += make_sdata_params(map_params)
    if op == make_sdata_op_call:
        caddr, method, types, values = operator
        d += make_sdata_handle_call(caddr, method, types, values)
    elif op == make_sdata_op_alg:
        svar, sop_tvars = operator
        d += make_sdata_handle_alg(svar, sop_tvars)
    elif op == make_sdata_op_balance:
        addr, = operator
        d += make_sdata_handle_balance(addr)
    elif op == make_sdata_op_gasprice:
        d += make_sdata_handle_gasprice()
    elif op == make_sdata_op_gasleft:
        d += make_sdata_handle_gasleft()
    elif op == make_sdata_op_cond:
        svar, sop, tvar, msg = operator
        d += make_sdata_handle_cond(svar, sop, tvar, msg)
    elif op == make_sdata_op_owner:
        addr, = operator
        d += make_sdata_handle_owner(addr)
    else:
        assert False, f'Invalid op - {op}'
    d += make_sdata_params(ref_params)
    return d

def make_sdata_ret(map_params, rdata):
    d = make_sdata_params(map_params)
    d += len(rdata).to_bytes(4, 'big') + rdata
    return d

def make_sdata_invoke(build_params, handles, ret):
    d = make_sdata_holder()
    d += make_sdata_params(build_params)
    handles_cnt = 0
    for handle in handles:
        if handle:
            if type(handle) is list:
                for sub_handle in handle:
                    if sub_handle:
                        handles_cnt += 1
            else:
                handles_cnt += 1
    d += handles_cnt.to_bytes(4, 'big')
    for handle in handles:
        if handle:
            if type(handle) is list:
                for sub_handle in handle:
                    if sub_handle:
                        if type(sub_handle) is bytes:
                            d += sub_handle
                        else:
                            op, map_params, operator, ref_params = sub_handle
                            d += make_sdata_handle(op, map_params, operator, ref_params)
            elif type(handle) is bytes:
                d += handle
            else:
                op, map_params, operator, ref_params = handle
                d += make_sdata_handle(op, map_params, operator, ref_params)
    if type(ret) is bytes:
        d += ret
    else:
        map_params, rdata = ret if ret else ([], b'')
        d += make_sdata_ret(map_params, rdata)
    return d

def make_sdata(types, values, invoke):
    types = types if types else []
    values = values if values else []
    types.append('bytes')
    if type(invoke) is bytes:
        idata = invoke
    else:
        build_params, handles, ret = invoke
        idata = make_sdata_invoke(build_params, handles, ret)
    values.append(idata)
    w3 = web3.Web3()
    return w3.keccak(text='invoke()')[:4] + w3.codec.encode(types, values)

if __name__ == '__main__':
    from format_helper import format_hex

    assert make_sdata_invoke([(1,0), (2,32), (3,64)], [b'\xaa'*32, b'\xbb'*32, b'\xcc'*32], b'\xff'*32).hex() == format_hex('''
        ## holder
        dc32c08af781414c33b1d3b42fb497679827654685f8ee3388e4623d21467dc3
        ## build_params
        # cnt
        00000003
        # idx[0]
        00000001
        # pos[0]
        00000000
        # idx[1]
        00000002
        # pos[1]
        00000020
        # idx[2]
        00000003
        # pos[2]
        00000040
        ## handles
        # cnt
        00000003
        # handle[0]
        aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
        # handle[1]
        bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
        # handle[2]
        cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
        # ret
        ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff
    '''), "make_sdata_invoke([(1,0), (2,32), (3,64)], [b'\xaa'*32, b'\xbb'*32, b'\xcc'*32], b'\xff'*32).hex() fail"

    assert make_sdata(['uint256', 'uint256', 'uint256'], [0x1111, 0x2222, 0x3333], b'\xee'*32).hex() == format_hex('''
        # method signature
        cab7f521
        # values[0]
        0000000000000000000000000000000000000000000000000000000000001111
        # values[1]
        0000000000000000000000000000000000000000000000000000000000002222
        # values[2]
        0000000000000000000000000000000000000000000000000000000000003333
        # idata
        00000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000020eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
    ''')
