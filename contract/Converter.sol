// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

library Converter {
  function bytesToUint8(bytes memory bs, uint ps) internal pure returns (uint8) {
    // return uint8(bs[ps]);

    uint256 val;
    assembly {
      val := mload(add(add(bs, 0x20), ps))
    }
    return uint8(val>>(256-8));
  }

  function bytesToUint16(bytes memory bs, uint ps) internal pure returns (uint16) {
    // uint16 val = 0;
    // for (uint8 i = 0; i < 2; ++i) {
    //   val |= uint16(uint8(bs[ps+i])) << (8*(2-i-1));
    // }
    // return val;

    uint256 val;
    assembly {
      val := mload(add(add(bs, 0x20), ps))
    }
    return uint16(val>>(256-16));
  }

  function bytesToUint24(bytes memory bs, uint ps) internal pure returns (uint24) {
    // uint24 val = 0;
    // for (uint8 i = 0; i < 3; ++i) {
    //   val |= uint24(uint8(bs[ps+i])) << (8*(3-i-1));
    // }
    // return val;

    uint256 val;
    assembly {
      val := mload(add(add(bs, 0x20), ps))
    }
    return uint24(val>>(256-24));
  }

  function bytesToUint32(bytes memory bs, uint ps) internal pure returns (uint32) {
    // uint32 val = 0;
    // for (uint8 i = 0; i < 4; ++i) {
    //   val |= uint32(uint8(bs[ps+i])) << (8*(4-i-1));
    // }
    // return val;

    uint256 val;
    assembly {
      val := mload(add(add(bs, 0x20), ps))
    }
    return uint32(val>>(256-32));
  }

  function bytesToUint256(bytes memory bs, uint ps) internal pure returns (uint256) {
    // uint256 val = 0;
    // for (uint8 i = 0; i < 32; ++i) {
    //   val |= uint256(uint8(bs[ps+i])) << (8*(32-i-1));
    // }
    // return val;

    uint256 val;
    assembly {
      val := mload(add(add(bs, 0x20), ps))
    }
    return val;
  }

  function bytesToAddress(bytes memory bs, uint ps) internal pure returns (address) {
    // uint160 val = 0;
    // for (uint8 i = 0; i < 20; ++i) {
    //   val |= uint160(uint8(bs[ps+i])) << (8*(20-i-1));
    // }
    // return address(val);

    uint256 val;
    assembly {
      val := mload(add(add(bs, 0x20), ps))
    }
    return address(uint160(val>>(256-160)));
  }

  function uint256ToBytes(bytes memory bs, uint ps, uint256 val) internal pure  {
    // for (uint8 i = 0; i < 32; i++) {
    //   uint8 v = uint8(val >> (8*(32-i-1)));
    //   bs[ps+i] = bytes1(v);
    // }

    assembly {
      mstore(add(add(bs, 0x20), ps), val)
    }
  }
}
