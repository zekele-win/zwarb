// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {Converter} from "./Converter.sol";
import {BytesLib} from "./BytesLib.sol";

// import {console} from "./console.sol";

contract Arb {
  uint256 internal constant HOLDER_TAG = 0xdc32c08af781414c33b1d3b42fb497679827654685f8ee3388e4623d21467dc3;
  address internal constant ADDR_COINBASE = address(0x0000000000000000000000000000000000000000);

  address _owner;

  constructor() {
    _owner = msg.sender;
  }

  function handle(bytes memory data, uint bp, uint256[] memory params) internal returns (uint) {
    // console.log("[arb] [handle] begin");

    uint32 op = Converter.bytesToUint32(data, bp); bp += 4;
    // console.log("[arb] [handle] bp", bp);
    // console.log("[arb] [handle] op", op);

    if (op == 0x00) { // call
      bp = handle_call(data, bp, params);
    } else if (op == 0x01) { // alg
      bp = handle_alg(data, bp, params);
    } else if (op == 0x02) { // balance
      bp = handle_balance(data, bp, params);
    } else if (op == 0x03) { // gasprice
      bp = handle_gasprice(data, bp, params);
    } else if (op == 0x04) { // gasleft
      bp = handle_gasleft(data, bp, params);
    } else if (op == 0x10) { // cond
      bp = handle_cond(data, bp, params);
    } else if (op == 0xff) { // cond
      bp = handle_owner(data, bp, params);
    } else {
      revert("handle fail");
    }

    // console.log("[arb] [handle] end");
    return bp;
  }

  function handle_call(bytes memory data, uint bp, uint256[] memory params) internal returns (uint) {
    // console.log("[arb] [handle_call] begin");

    bp = map_params(data, bp, params);

    address caddr = Converter.bytesToAddress(data, bp); bp += 20;
    // console.log("[arb] [handle_call] bp", bp);
    // console.log("[arb] [handle_call] caddr", caddr);
    if (caddr == ADDR_COINBASE) {
      caddr = block.coinbase;
      // console.log("[arb] [handle_call] caddr", caddr);
    }

    uint32 elen = Converter.bytesToUint32(data, bp); bp += 4;
    // console.log("[arb] [handle_call] bp", bp);
    // console.log("[arb] [handle_call] elen", elen);

    // bytes memory edata = new bytes(elen);
    // for (uint32 i = 0; i < elen; i++) {
    //   edata[i] = data[bp+i];
    // }
    bytes memory edata = BytesLib.slice(data, bp, elen);
    bp += elen;
    // console.log("[arb] [handle_call] bp", bp);
    // console.log("[arb] [handle_call] edata"); console.logBytes(edata);

    (bool success, bytes memory result) = caddr.call{value: params[0]}(edata);
    // console.log("[arb] [handle_call] caddr.call", success); console.logBytes(result);
    // require(success, string.concat("handle_call fail ", string(result)));
    require(success, string.concat("handle_call fail ", BytesLib.toHex(result)));

    params[0] = 0;

    bp = ref_params(data, bp, params, result);

    // console.log("[arb] [handle_call] end");
    return bp;
  }

  function handle_alg(bytes memory data, uint bp, uint256[] memory params) internal pure returns (uint) {
    // console.log("[arb] [handle_alg] begin");

    bp = map_params(data, bp, params);

    uint256 svar = Converter.bytesToUint256(data, bp); bp += 32;
    // console.log("[arb] [handle_alg] bp", bp);
    // console.log("[arb] [handle_alg] svar", svar);

    uint32 cnt = Converter.bytesToUint32(data, bp); bp += 4;
    // console.log("[arb] [handle_alg] bp", bp);
    // console.log("[arb] [handle_alg] cnt", cnt);

    for (uint32 i = 0; i < cnt; i++) {
      uint32 sop = Converter.bytesToUint32(data, bp); bp += 4;
      // console.log("[arb] [handle_alg] bp", bp);
      // console.log("[arb] [handle_alg] sop", sop);

      uint256 tvar = Converter.bytesToUint256(data, bp); bp += 32;
      // console.log("[arb] [handle_alg] bp", bp);
      // console.log("[arb] [handle_alg] tvar", tvar);

      if (sop == 0x01) { // Add
        svar += tvar;
      } else if (sop == 0x02) { // Sub
        require(svar >= tvar, "handle_alg fail sub");
        svar -= tvar;
      } else if (sop == 0x03) { // Mul
        svar *= tvar;
      } else if (sop == 0x04) { // Div
        require(tvar > 0, "handle_alg fail div");
        svar /= tvar;
      } else {
        revert("handle_alg fail");
      }
      // console.log("[arb] [handle_alg] svar", svar);
    }

    bp = ref_params(data, bp, params, svar);

    // console.log("[arb] [handle_alg] end");
    return bp;
  }

  function handle_balance(bytes memory data, uint bp, uint256[] memory params) internal view returns (uint) {
    // console.log("[arb] [handle_balance] begin");

    bp = map_params(data, bp, params);

    address addr = Converter.bytesToAddress(data, bp); bp += 20;
    // console.log("[arb] [handle_balance] bp", bp);
    // console.log("[arb] [handle_balance] addr", addr);
    if (addr == ADDR_COINBASE) {
      addr = block.coinbase;
      // console.log("[arb] [handle_balance] addr", addr);
    }

    uint256 svar = addr.balance;
    // console.log("[arb] [handle_balance] svar", svar);

    bp = ref_params(data, bp, params, svar);

    // console.log("[arb] [handle_balance] end");
    return bp;
  }

  function handle_gasprice(bytes memory data, uint bp, uint256[] memory params) internal view returns (uint) {
    // console.log("[arb] [handle_gasprice] begin");

    bp = map_params(data, bp, params);

    uint256 svar = tx.gasprice;
    // console.log("[arb] [handle_gasprice] svar", svar);

    bp = ref_params(data, bp, params, svar);

    // console.log("[arb] [handle_gasprice] end");
    return bp;
  }

  function handle_gasleft(bytes memory data, uint bp, uint256[] memory params) internal view returns (uint) {
    // console.log("[arb] [handle_gasleft] begin");

    bp = map_params(data, bp, params);

    uint256 svar = gasleft();
    // console.log("[arb] [handle_gasleft] svar", svar);

    bp = ref_params(data, bp, params, svar);

    // console.log("[arb] [handle_gasleft] end");
    return bp;
  }

  function handle_cond(bytes memory data, uint bp, uint256[] memory params) internal pure returns (uint) {
    // console.log("[arb] [handle_cond] begin");

    bp = map_params(data, bp, params);

    uint256 svar = Converter.bytesToUint256(data, bp); bp += 32;
    // console.log("[arb] [handle_cond] bp", bp);
    // console.log("[arb] [handle_cond] svar", svar);

    uint32 sop = Converter.bytesToUint32(data, bp); bp += 4;
    // console.log("[arb] [handle_cond] bp", bp);
    // console.log("[arb] [handle_cond] sop", sop);

    uint256 tvar = Converter.bytesToUint256(data, bp); bp += 32;
    // console.log("[arb] [handle_cond] bp", bp);
    // console.log("[arb] [handle_cond] tvar", tvar);

    uint32 elen = Converter.bytesToUint32(data, bp); bp += 4;
    // console.log("[arb] [handle_cond] bp", bp);
    // console.log("[arb] [handle_cond] elen", elen);

    // bytes memory edata = new bytes(elen);
    // for (uint32 i = 0; i < elen; i++) {
    //   edata[i] = data[bp+i];
    // }
    bytes memory edata = BytesLib.slice(data, bp, elen);
    bp += elen;
    // console.log("[arb] [handle_cond] bp", bp);
    // console.log("[arb] [handle_cond] edata"); console.logBytes(edata);

    string memory emsg = string(edata);
    // console.log("[arb] [handle_cond] emsg", emsg);

    if (sop == 0x01) { // ==
      require(svar == tvar, emsg);
    } else if (sop == 0x02) { // <
      require(svar < tvar, emsg);
    } else if (sop == 0x03) { // <=
      require(svar <= tvar, emsg);
    } else if (sop == 0x04) { // >
      require(svar > tvar, emsg);
    } else if (sop == 0x05) { // >=
      require(svar >= tvar, emsg);
    } else {
      revert("handle_cond fail");
    }

    bp = ref_params(data, bp);

    // console.log("[arb] [handle_cond] end");
    return bp;
  }

  function handle_owner(bytes memory data, uint bp, uint256[] memory params) internal returns (uint) {
    // console.log("[arb] [handle_owner] begin");

    bp = map_params(data, bp, params);

    address addr = Converter.bytesToAddress(data, bp); bp += 20;
    // console.log("[arb] [handle_owner] bp", bp);
    // console.log("[arb] [handle_owner] addr", addr);

    _owner = addr;

    bp = ref_params(data, bp);

    // console.log("[arb] [handle_owner] end");
    return bp;
  }

  function ref_params(bytes memory data, uint bp) internal pure returns (uint) {
    // console.log("[arb] [ref_params] begin");

    uint32 cnt = Converter.bytesToUint32(data, bp); bp += 4;
    // console.log("[arb] [ref_params] bp", bp);
    // console.log("[arb] [ref_params] cnt", cnt);
    require(cnt == 0, "ref_params from null fail");

    // console.log("[arb] [ref_params] end");
    return bp;
  }

  function ref_params(bytes memory data, uint bp, uint256[] memory params, uint256 svar) internal pure returns (uint) {
    // console.log("[arb] [ref_params] begin");

    uint32 cnt = Converter.bytesToUint32(data, bp); bp += 4;
    // console.log("[arb] [ref_params] bp", bp);
    // console.log("[arb] [ref_params] cnt", cnt);

    for (uint32 i = 0; i < cnt; i++) {
      uint32 idx = Converter.bytesToUint32(data, bp); bp += 4;
      // console.log("[arb] [ref_params] bp", bp);
      // console.log("[arb] [ref_params] idx", idx);
      uint32 pos = Converter.bytesToUint32(data, bp); bp += 4;
      // console.log("[arb] [ref_params] bp", bp);
      // console.log("[arb] [ref_params] pos", pos);
      require(pos == 0, "ref_params from savr fail");
      params[idx] = svar;
    }
    // console.log("[arb] [ref_params] params"); for (uint i = 0; i < params.length; i++) console.log(i, params[i]);

    // console.log("[arb] [ref_params] end");
    return bp;
  }

  function ref_params(bytes memory data, uint bp, uint256[] memory params, bytes memory result) internal pure returns (uint) {
    // console.log("[arb] [ref_params] begin");

    uint32 cnt = Converter.bytesToUint32(data, bp); bp += 4;
    // console.log("[arb] [ref_params] bp", bp);
    // console.log("[arb] [ref_params] cnt", cnt);

    for (uint32 i = 0; i < cnt; i++) {
      uint32 idx = Converter.bytesToUint32(data, bp); bp += 4;
      // console.log("[arb] [ref_params] bp", bp);
      // console.log("[arb] [ref_params] idx", idx);
      uint32 pos = Converter.bytesToUint32(data, bp); bp += 4;
      // console.log("[arb] [ref_params] bp", bp);
      // console.log("[arb] [ref_params] pos", pos);
      uint256 svar = Converter.bytesToUint256(result, pos);
      // console.log("[arb] [ref_params] svar", svar);
      params[idx] = svar;
    }
    // console.log("[arb] [ref_params] params"); for (uint i = 0; i < params.length; i++) console.log(i, params[i]);

    // console.log("[arb] [ref_params] end");
    return bp;
  }

  function map_params(bytes memory data, uint bp, uint256[] memory params) internal pure returns (uint) {
    // console.log("[arb] [map_params] begin");

    uint32 cnt = Converter.bytesToUint32(data, bp); bp += 4;
    // console.log("[arb] [map_params] bp", bp);
    // console.log("[arb] [map_params] cnt", cnt);

    uint offset = bp + cnt * 8;
    // console.log("[arb] [map_params] offset", offset);

    for (uint32 i = 0; i < cnt; i++) {
      uint32 idx = Converter.bytesToUint32(data, bp); bp += 4;
      // console.log("[arb] [map_params] bp", bp);
      // console.log("[arb] [map_params] idx", idx);
      uint32 pos = Converter.bytesToUint32(data, bp); bp += 4;
      // console.log("[arb] [map_params] bp", bp);
      // console.log("[arb] [map_params] pos", pos);
      uint256 svar = params[idx];
      // console.log("[arb] [map_params] svar", svar);
      Converter.uint256ToBytes(data, offset + pos, svar);
    }

    // console.log("[arb] [map_params] end");
    return bp;
  }

  function build_params(bytes memory data, uint bp, uint256[] memory params) internal pure returns (uint) {
    // console.log("[arb] [build_params] begin");

    uint32 cnt = Converter.bytesToUint32(data, bp); bp += 4;
    // console.log("[arb] [build_params] bp", bp);
    // console.log("[arb] [build_params] cnt", cnt);

    for (uint32 i = 0; i < cnt; i++) {
      uint32 idx = Converter.bytesToUint32(data, bp); bp += 4;
      // console.log("[arb] [build_params] bp", bp);
      // console.log("[arb] [build_params] idx", idx);
      uint32 pos = Converter.bytesToUint32(data, bp); bp += 4;
      // console.log("[arb] [build_params] bp", bp);
      // console.log("[arb] [build_params] pos", pos);
      uint256 svar = Converter.bytesToUint256(data, pos);
      // console.log("[arb] [build_params] svar", svar);
      params[idx] = svar;
    }
    // console.log("[arb] [build_params] params"); for (uint i = 0; i < params.length; i++) console.log(i, params[i]);

    // console.log("[arb] [build_params] end");
    return bp;
  }

  function find_holder(bytes memory data, uint bp) internal pure returns (uint) {
    // console.log("[arb] [find_holder] begin");

    while (bp < data.length) {
      uint256 holder = Converter.bytesToUint256(data, bp); bp += 32;
      if (holder == HOLDER_TAG) {
        // console.log("[arb] [find_holder] bp", bp);
        // console.log("[arb] [find_holder] end");
        return bp;
      }
    }

    revert("find_holder fail");
  }

  function invoke(bytes memory data, uint bp, uint256[] memory params) internal returns (uint) {
    // console.log("[arb] [invoke] begin");

    bp = find_holder(data, bp);

    bp = build_params(data, bp, params);

    uint32 cnt = Converter.bytesToUint32(data, bp); bp += 4;
    // console.log("[arb] [invoke] bp", bp);
    // console.log("[arb] [invoke] cnt", cnt);

    for (uint32 i = 0; i < cnt; i++) {
      bp = handle(data, bp, params);
    }

    // console.log("[arb] [invoke] end");
    return bp;
  }

  function ret(bytes memory data, uint bp, uint256[] memory params) internal pure returns (uint, uint) {
    // console.log("[arb] [ret] begin");

    bp = map_params(data, bp, params);
    uint32 rlen = Converter.bytesToUint32(data, bp); bp += 4;
    // console.log("[arb] [ret] bp", bp);
    // console.log("[arb] [ret] rlen", rlen);

    // console.log("[arb] [ret] end");
    return (bp, rlen);
  }

  fallback() external payable {
    require(tx.origin == _owner, "invalid owner");

    // console.log("[arb] [fallback] msg", msg.value); console.logBytes(msg.data);

    uint256[] memory params = new uint256[](8);

    bytes memory data = msg.data[4:];
    uint bp = invoke(data, 0, params);
    uint rlen;
    (bp, rlen) = ret(data, bp, params);
    if (rlen > 0) {
      assembly {
        return(add(add(data, 0x20), bp), rlen)
      }
    }
  }

  receive() external payable {
    // console.log("[arb] [receive] msg.value", msg.value);
  }
}
