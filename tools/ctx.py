#!/usr/bin/env python3
# 打印指定地址前 back 条、后 fwd 条指令（带上下文，最常用）
# 用法: python ctx.py <elf文件> <十六进制地址> <back> <fwd>
import sys
from capstone import CS_ARCH_PPC, CS_MODE_64, CS_MODE_BIG_ENDIAN, Cs

BASE = 0x10000


def main():
    if len(sys.argv) < 5:
        print("用法: ctx.py <elf> <addr> <back> <fwd>")
        return
    data = open(sys.argv[1], 'rb').read()
    md = Cs(CS_ARCH_PPC, CS_MODE_64 | CS_MODE_BIG_ENDIAN)
    md.skipdata = True
    addr = int(sys.argv[2], 16)
    back, fwd = int(sys.argv[3]), int(sys.argv[4])
    start = addr - back * 4
    off = start - BASE
    for i in md.disasm(data[off:off + (back + fwd) * 4], start):
        mark = ' <==' if i.address == addr else ''
        print("  0x%x: %-24s %s%s" % (i.address, i.mnemonic, i.op_str, mark))


if __name__ == '__main__':
    main()
