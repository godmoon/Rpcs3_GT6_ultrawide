#!/usr/bin/env python3
# PS3 PKG 解包器（按 RPCS3 unpkg.cpp 的实现移植）
# 仅处理零售(release)包：AES-128-ECB 计数器流加密
import struct, sys, os
from Crypto.Cipher import AES

KEY = bytes.fromhex('2e7b71d7c9c9a14ea3221f188828b8f8')


class Pkg:
    def __init__(self, path):
        self.path = path
        self.f = open(path, 'rb')
        h = self.f.read(0xC0)
        self.magic = h[0:4]
        self.pkg_type, self.platform = struct.unpack('>HH', h[4:8])
        self.meta_offset, self.meta_count, self.meta_size, self.file_count = \
            struct.unpack('>IIII', h[8:0x18])
        self.pkg_size, self.data_offset, self.data_size = \
            struct.unpack('>QQQ', h[0x18:0x30])
        self.title_id = h[0x30:0x60].split(b'\0')[0].decode()
        klic = h[0x70:0x80]
        self.counter0 = int.from_bytes(klic, 'big')
        self.aes = AES.new(KEY, AES.MODE_ECB)
        self._ks_pos = None
        self._ks = b''

    def _keystream(self, start, n):
        # 生成从字节位置 start 开始、长 n 的密钥流
        b0 = start // 16
        pad = start % 16
        nb = (pad + n + 15) // 16
        out = bytearray()
        for i in range(nb):
            c = (self.counter0 + b0 + i) & ((1 << 128) - 1)
            out += self.aes.encrypt(c.to_bytes(16, 'big'))
        return bytes(out[pad:pad + n])

    def read(self, off, size):
        self.f.seek(self.data_offset + off)
        d = self.f.read(size)
        ks = self._keystream(off, len(d))
        return bytes(a ^ b for a, b in zip(d, ks))

    def entries(self):
        raw = self.read(0, self.file_count * 0x20)
        out = []
        for i in range(self.file_count):
            no, ns, fo, fs, ty, _ = struct.unpack('>IIQQII', raw[i*0x20:(i+1)*0x20])
            name = self.read(no, ns).rstrip(b'\0').decode('utf-8', 'replace')
            out.append((name, fo, fs, ty))
        return out


def main(pkg_path, outdir):
    p = Pkg(pkg_path)
    print(f"magic={p.magic} type=0x{p.pkg_type:04x} platform={p.platform} "
          f"title={p.title_id} files={p.file_count} data=0x{p.data_size:x}")
    os.makedirs(outdir, exist_ok=True)
    for name, fo, fs, ty in p.entries():
        rel = name.lstrip('/')
        dst = os.path.join(outdir, rel)
        if ty & 0xff == 4 or fs == 0 and ty & 0xff == 4:
            os.makedirs(dst, exist_ok=True)
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'wb') as f:
            pos = 0
            while pos < fs:
                n = min(1 << 20, fs - pos)
                f.write(p.read(fo + pos, n))
                pos += n
        print(f"  type={ty & 0xff} size={fs:>9} {rel}")


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
