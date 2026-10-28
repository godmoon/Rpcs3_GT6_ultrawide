#!/usr/bin/env python3
# 反查函数指针引用：代码地址 -> .opd 描述符 -> 引用该描述符的位置（虚表/函数指针表）
# 用法: python opdxref.py <elf文件> <代码地址...>
# 背景: PS3 的 PPC64 ELF 里，函数指针指向 .opd 描述符 {u32 code, u32 toc}，
#       所以 bl 扫描不到的函数（虚函数）要通过 .opd 反向查找。
import struct
import sys

BASE = 0x10000
OPD_LO, OPD_HI = 0x148e2d0, 0x14e5560


def main():
    if len(sys.argv) < 3:
        print("用法: opdxref.py <elf> <代码地址...>")
        return
    data = open(sys.argv[1], 'rb').read()

    def u32(va):
        return struct.unpack('>I', data[va - BASE:va - BASE + 4])[0]

    for arg in sys.argv[2:]:
        tgt = int(arg, 16)
        descs = [va for va in range(OPD_LO, OPD_HI, 8) if u32(va) == tgt]
        print("代码 0x%x 的 .opd 描述符: %s" % (tgt, ' '.join('0x%x' % d for d in descs)))
        for d in descs:
            needle = struct.pack('>I', d)
            hits = []
            start = 0
            while True:
                i = data.find(needle, start)
                if i < 0:
                    break
                hits.append(i + BASE)
                start = i + 1
            print("   描述符 0x%x 被引用 %d 次: %s"
                  % (d, len(hits), ' '.join('0x%x' % h for h in hits[:20])))
            for h in hits[:6]:
                print("     0x%x 附近: %s" % (h, ' '.join('%08x' % u32(h - 16 + 4 * k) for k in range(12))))


if __name__ == '__main__':
    main()
