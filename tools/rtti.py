#!/usr/bin/env python3
# 解析 PS3 ELF 的 RTTI 类型信息与 vtable，输出类名到方法代码地址的映射
import struct, sys

class Elf:
    def __init__(self, path):
        self.d = open(path, 'rb').read()
        self.base = 0x10000  # 本 ELF 中 va = file_off + 0x10000

    def u32(self, va):
        o = va - self.base
        if o < 0 or o + 4 > len(self.d):
            return None
        return struct.unpack_from('>I', self.d, o)[0]

    def cstr(self, va, maxlen=200):
        o = va - self.base
        if o < 0 or o >= len(self.d):
            return ''
        e = self.d.find(b'\0', o, o + maxlen)
        if e < 0:
            e = o + maxlen
        return self.d[o:e].decode('latin1')

    def opd(self, desc):
        # .opd 描述符：{u32 code, u32 toc}
        if self.u32(desc) is None or self.u32(desc + 4) is None:
            return None
        return self.u32(desc), self.u32(desc + 4)


def main(path, lo, hi):
    e = Elf(path)
    va = lo
    found = 0
    while va < hi:
        ti = e.u32(va - 4)
        ok = ti is not None and 0x1400000 <= ti < 0x14e5560
        if ok:
            nptr = e.u32(ti + 4)
            name = e.cstr(nptr) if nptr else ''
            if name.startswith('N') and name.endswith('E'):
                ms = []
                p = va
                while p - va < 0x100:
                    m = e.u32(p)
                    if m is None or m == 0 or not (0x1400000 <= m < 0x14e5560):
                        break
                    o = e.opd(m)
                    ms.append((m, o[0] if o else None))
                    p += 4
                vt = e.opd(va)
                print('vtable 0x%x (code 0x%x) ti=0x%x %s' % (va, vt[0] if vt else 0, ti, name))
                print('   methods:', ' '.join('0x%x' % (c or 0) for _, c in ms))
                found += 1
                va = max(p, va + 4)
                continue
        va += 4
    print('total', found)


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2], 0), int(sys.argv[3], 0))
