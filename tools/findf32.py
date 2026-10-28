#!/usr/bin/env python3
# 在 ELF 里查找某个 32 位大端浮点数出现的所有位置（含上下文，方便判断是不是常量池）
# 用法: python findf32.py <elf文件> <浮点值> [上下文个数]
#   例: python findf32.py EMAIN.100.elf 1.7777778 8
#   例: python findf32.py EMAIN.100.elf 1.0 4
import struct
import sys

BASE = 0x10000


def main():
    if len(sys.argv) < 3:
        print("用法: findf32.py <elf> <浮点值> [上下文个数]")
        return
    data = open(sys.argv[1], 'rb').read()
    val = struct.unpack('>f', struct.pack('>f', float(sys.argv[2])))[0]
    ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    needle = struct.pack('>f', val)

    hits = []
    start = 0
    while True:
        i = data.find(needle, start)
        if i < 0:
            break
        hits.append(i + BASE)
        start = i + 4

    # 带对齐过滤：常量的地址基本都是 4 字节对齐
    aligned = [h for h in hits if h % 4 == 0]
    print("值 %.9g (0x%08x) 共出现 %d 次，其中 4 字节对齐 %d 次"
          % (val, struct.unpack('>I', needle)[0], len(hits), len(aligned)))

    for h in aligned:
        off = h - BASE
        lo = off - 4 * (ctx // 2)
        print("== 0x%x" % h)
        for k in range(ctx):
            a = lo + 4 * k
            if a < 0 or a + 4 > len(data):
                continue
            f = struct.unpack_from('>f', data, a)[0]
            u = struct.unpack_from('>I', data, a)[0]
            mark = '  <==' if a == off else ''
            print("   0x%x: %08x  %-16.8g%s" % (a + BASE, u, f, mark))


if __name__ == '__main__':
    main()
