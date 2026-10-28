#!/usr/bin/env python3
# 按 RPCS3 的算法计算 PPU executable hash（用于 patch YAML 的 PPU-xxxx 键）
# 算法来源：rpcs3/Emu/Cell/PPUModule.cpp，遍历 program header：
#   对每个 phdr: sha1(p_type BE32) + sha1(p_flags BE32)
#   若 p_type==PT_LOAD 且 p_memsz: sha1(p_vaddr BE32) + sha1(p_memsz BE32) + sha1(段数据 p_filesz 字节)
import struct, hashlib, sys

p = sys.argv[1]
d = open(p, 'rb').read()
assert d[:4] == b'\x7fELF', '不是 ELF 文件'
is64 = d[4] == 2
end = '>' if d[5] == 2 else '<'      # PS3 为 big-endian(2)
if is64:
    e_phoff, = struct.unpack_from(end + 'Q', d, 0x20)
    e_phentsize, e_phnum = struct.unpack_from(end + 'HH', d, 0x36)
else:
    e_phoff, = struct.unpack_from(end + 'I', d, 0x1C)
    e_phentsize, e_phnum = struct.unpack_from(end + 'HH', d, 0x2A)

h = hashlib.sha1()
for i in range(e_phnum):
    o = e_phoff + i * e_phentsize
    if is64:
        p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from(end + 'IIQQQQQQ', d, o)
    else:
        p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = struct.unpack_from(end + 'IIIIIIII', d, o)
    h.update(struct.pack(end + 'I', p_type))
    h.update(struct.pack(end + 'I', p_flags))
    if p_type == 0x1 and p_memsz:
        # RPCS3 用 sizeof(prog.p_vaddr)/sizeof(prog.p_memsz)，ELF64 下各 8 字节
        fmt = end + ('Q' if is64 else 'I')
        h.update(struct.pack(fmt, p_vaddr))
        h.update(struct.pack(fmt, p_memsz))
        h.update(d[p_offset:p_offset + p_filesz])

print('PPU-%s' % h.hexdigest())
