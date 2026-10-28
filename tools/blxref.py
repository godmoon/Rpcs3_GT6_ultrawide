#!/usr/bin/env python3
# 扫描 .text 中所有 bl 指令，统计调用指定目标地址的位置
# 用法: python blxref.py <elf文件> <目标地址...>
# 用途: 普通 bl 扫描不到时，说明该函数是通过函数指针/虚表调用的，改用 opdxref.py 反查 .opd
import struct
import sys

BASE = 0x10000
TEXT_START, TEXT_END = 0x10230, 0xf908c4


def main():
    if len(sys.argv) < 3:
        print("用法: blxref.py <elf> <目标地址...>")
        return
    data = open(sys.argv[1], 'rb').read()
    targets = {int(a, 16) for a in sys.argv[2:]}
    res = {t: [] for t in targets}

    code = data[TEXT_START - BASE:TEXT_END - BASE]
    for off in range(0, len(code) - 3, 4):
        w = struct.unpack_from('>I', code, off)[0]
        if (w >> 26) != 18:          # 只要 bl
            continue
        va = TEXT_START + off
        if w & 1:                    # AA=1 绝对地址
            tgt = w & 0x03FFFFFC
        else:                        # AA=0 相对地址
            li = w & 0x03FFFFFC
            if li & 0x02000000:
                li -= 0x04000000
            tgt = (va + li) & 0xFFFFFFFF
        if tgt in res:
            res[tgt].append(va)

    for t in sorted(res):
        print("bl 0x%x 调用点 %d 个: %s" % (t, len(res[t]), ' '.join('0x%x' % a for a in res[t][:40])))


if __name__ == '__main__':
    main()
