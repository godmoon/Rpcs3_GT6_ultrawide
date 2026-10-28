#!/usr/bin/env python3
# 反汇编 PS3 ELF(PPU) 中指定虚拟地址附近
# 用法: python ppcdis.py <elf文件> <十六进制地址> [更多地址...]
# 说明: 本 ELF 满足 va = 文件偏移 + 0x10000
import sys
from capstone import CS_ARCH_PPC, CS_MODE_64, CS_MODE_BIG_ENDIAN, Cs

BASE = 0x10000


def main():
    if len(sys.argv) < 3:
        print(__doc__ if __doc__ else "用法: ppcdis.py <elf> <addr> ...")
        return
    data = open(sys.argv[1], 'rb').read()
    md = Cs(CS_ARCH_PPC, CS_MODE_64 | CS_MODE_BIG_ENDIAN)
    md.skipdata = True
    for arg in sys.argv[2:]:
        va = int(arg, 16)
        print("===== 0x%x" % va)
        off = va - BASE
        for i in md.disasm(data[off:off + 200], va):
            print("0x%x: %-10s %-10s %s" % (i.address, i.bytes.hex(), i.mnemonic, i.op_str))


if __name__ == '__main__':
    main()
