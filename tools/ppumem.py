#!/usr/bin/env python3
# 在 RPCS3 进程内存中定位 PPU 地址空间基址，并提供按 PPU 地址读写的能力。
# 原理：ELF 的 va 就是 PPU 地址；在宿主进程里找到 .rodata 中某个唯一字符串，
# 相减即得基址。
import os, re, struct, sys

MARKER = b'monitor_aspect_ratio\x00'
MARKER_VA = 0xfbfd80

def maps(pid):
    out = []
    with open(f'/proc/{pid}/maps') as f:
        for line in f:
            m = re.match(r'([0-9a-f]+)-([0-9a-f]+) (\S{4}) \S+ \S+ \S+\s*(.*)', line)
            if not m:
                continue
            a, b, perm, path = int(m.group(1), 16), int(m.group(2), 16), m.group(3), m.group(4)
            out.append((a, b, perm, path))
    return out

def find_base(pid):
    fd = os.open(f'/proc/{pid}/mem', os.O_RDONLY)
    try:
        for a, b, perm, path in maps(pid):
            if perm[0] != 'r' or b - a > 0x40000000:
                continue
            try:
                os.lseek(fd, a, os.SEEK_SET)
            except OSError:
                continue
            pos = a
            step = 1 << 21
            tail = b''
            while pos < b:
                try:
                    chunk = os.pread(fd, min(step, b - pos), pos)
                except OSError:
                    break
                if not chunk:
                    break
                data = tail + chunk
                i = data.find(MARKER)
                if i >= 0:
                    host = pos - len(tail) + i
                    return host - MARKER_VA
                tail = data[-64:]
                pos += len(chunk)
    finally:
        os.close(fd)
    return None

class Ppu:
    def __init__(self, pid):
        self.pid = pid
        self.base = find_base(pid)
        if self.base is None:
            raise SystemExit('未找到 PPU 基址')
        self.rfd = os.open(f'/proc/{pid}/mem', os.O_RDONLY)
        self.wfd = os.open(f'/proc/{pid}/mem', os.O_RDWR)

    def read(self, va, n):
        return os.pread(self.rfd, n, self.base + va)

    def write(self, va, data):
        return os.pwrite(self.wfd, data, self.base + va)

    def f32(self, va):
        return struct.unpack('>f', self.read(va, 4))[0]

    def set_f32(self, va, v):
        self.write(va, struct.pack('>f', v))

if __name__ == '__main__':
    pid = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.popen('pgrep -x rpcs3 | head -1').read())
    p = Ppu(pid)
    print('pid=%d base=0x%x' % (pid, p.base))
    for va in [0xfbfd80, 0xfbc980, 0xfdf690, 0xff4b18]:
        print('  0x%x: %s' % (va, p.read(va, 4).hex(' ')), end='')
        if va != 0xfbfd80:
            print('  float=%g' % p.f32(va))
        else:
            print('  %r' % p.read(va, 20))
