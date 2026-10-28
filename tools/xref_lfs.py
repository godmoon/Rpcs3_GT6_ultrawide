#!/usr/bin/env python3
# 扫描 .text 中 lis + lfs/lfd/lwz/ld 组合，找出对指定常量池地址的引用
# 用法: python xref_lfs.py <elf文件> [目标地址...]
#   不给目标时，默认查 8 个已知的 1.7777778f 常量池地址
# 注意: 全量扫描约 40 万条指令，需要 2~5 分钟；可先用 findf32.py 缩小范围
from capstone import CS_ARCH_PPC, CS_MODE_64, CS_MODE_BIG_ENDIAN, CS_AC_WRITE, Cs
from capstone.ppc import PPC_OP_MEM, PPC_OP_REG

BASE = 0x10000
TEXT_START, TEXT_END = 0x10230, 0xf908c4

DEFAULT_TARGETS = [
    0xfbc980, 0xfdf690, 0xff4b18, 0x100531c,
    0x1005a3c, 0x1012178, 0x1039aac, 0x103d360,
]


def main():
    import sys
    if len(sys.argv) < 2:
        print("用法: xref_lfs.py <elf> [目标地址...]")
        return
    data = open(sys.argv[1], 'rb').read()
    targets = {int(a, 16) for a in sys.argv[2:]} or set(DEFAULT_TARGETS)

    code = data[TEXT_START - BASE:TEXT_END - BASE]
    md = Cs(CS_ARCH_PPC, CS_MODE_64 | CS_MODE_BIG_ENDIAN)
    md.detail = True
    md.skipdata = True

    res = []
    window = []   # [寄存器, 高16位基址, lis地址, 是否已被改写]
    count = 0
    for ins in md.disasm(code, TEXT_START):
        count += 1
        if ins.mnemonic == "lis":
            try:
                window.append([ins.operands[0].reg,
                               (ins.operands[1].imm & 0xffff) << 16,
                               ins.address, 0])
            except Exception:
                pass
        else:
            try:
                for op in ins.operands:
                    if op.type == PPC_OP_REG and (op.access & CS_AC_WRITE):
                        for w in window:
                            if w[0] == op.reg:
                                w[3] = 1
            except Exception:
                pass

        if ins.mnemonic in ("lfs", "lfd", "lwz", "ld") and len(ins.operands) == 2 \
                and ins.operands[1].type == PPC_OP_MEM:
            base = ins.operands[1].mem.base
            disp = ins.operands[1].mem.disp
            for w in window:
                if w[0] == base and not w[3]:
                    addr = (w[1] + disp) & 0xffffffff
                    if addr in targets:
                        res.append((w[2], ins.address, ins.mnemonic, ins.op_str, addr))
        if len(window) > 200:
            window = window[-200:]

    print("指令数", count)
    seen = set()
    for r in res:
        key = (r[1], r[4])
        if key in seen:      # 同一个加载点可能被多个 lis 命中，去重
            continue
        seen.add(key)
        print("lis@0x%x -> %s@0x%x %s  => 常量 0x%x" % (r[0], r[2], r[1], r[3], r[4]))
    print("引用总数", len(seen))
    for t in sorted(targets):
        n = sum(1 for r in seen if r[1] == t)
        print("  0x%x 命中 %d 处" % (t, n))


if __name__ == '__main__':
    main()
