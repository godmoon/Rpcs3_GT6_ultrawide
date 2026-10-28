# How To Build / Port This Patch

本文件记录把 GT6 超宽屏 patch 从一个新版本的 `EMAIN.SELF` 上做出来的正确方式，供后续新版本使用。

## A. 基本概念

- RPCS3 patch 的形式是 `PPU-<hash>` + patch entries。
- `bef32` 直接将 32-bit 成员写满给定 PPU 地址。
- Patch 在 `ppu_load_exec` 时写入，热修改无效。

## B. 需要的输入

至少要有：
- 对应版本的 ISO / `EBOOT.BIN` + `EMAIN.SELF`
- 或已更新到的 PKG USRDIR
- `ppuhash.py` 或 RPCS3.log，确认 `PPU-<hash>`
- Python 3 / 一定程度的数据分析能力
- 对照图

## C. 第一步：确认 PPU hash

### 方法 1
用 RPCS3 跑一次，从日志里拿：

```text
PPU executable hash: PPU-xxxxxxxxxxxxxxxx...
```

### 方法 2
把 SELF 解密成 ELF 并用 `ppuhash.py` 确认 hash。

## D. 第二步：定位 1.7777778f 常量

### 1. 扫描 floats
在 EMAIN.elf 中找全部 `1.7777778` 的 4 字节对齐出现位置。

### 2. 不用“所有”地址都 patch
优先从大表（section 4）找到：
- `0x... SimpleCamera`
- `getAspect` / `monitor_aspect_ratio`
- `resolution branch`
- 2D / HUD 需要对照图

### 3. runtime 兜底（ safer ）
如果不确定，可以在 Windows/Linux 下做运行时内存扫描：

1. 启动 RPCS3 + 游戏  
2. OpenProcess + VirtualQueryEx
3. 找 marker 字符串 `monitor_aspect_ratio`
4. 按 segment 偏移套 base
5. 找 `3FE38E39` 的 aligned occurrence
6. 数量应为 16（GT6 1.00 / 1.05 已经如此）

### 4. memory patch test
写 Python 脚本，直接 `set_f32` 或 `WriteProcessMemory` 3.5555556 看是否变化。

### 5. commit 地址
把 confirmed addresses 写入 patch YAML。

## E. YAML 格式

```yaml
Version: 1.2

PPU-<hash>:
  "32:9 UWW (GT6 <version>, 16 constants)":
    Games:
      "Gran Turismo 6":
        BCAS25018: [ <01.xx> ]
    Author: "gt6-uw"
    Notes: "..."
    Patch Version: 1.0
    Patch:
      - [ bef32, 0x<address>, 3.5555556 ]
```

### 必要文件名
RPCS3 只加载：`patches/<SERIAL>_patch.yml`  
也就是 `BCAS25018_patch.yml`。

## F. 1.05 例子

- hash: `PPU-824c9dd3c8f7de8b5060ec99b06f474de274de35`
- 16 address list:
  ```
  0x01024cc0
  0x01044ef8
  0x01044f1c
  0x010453f8
  0x01048374
  0x01053474
  0x01053488
  0x0106497c
  0x0106504c
  0x010717a0
  0x0109edd4
  0x010a2648
  0x010dba1c
  0x010dc7c8
  0x010dc7f8
  0x010dd5d0
  ```

## G. 风险与建议

- 不要在 1.00 与 1.05 混用地址
- patch 严格 `one at a time`
- 先做 TEST 0，再做 subset
- 用驾驶学校 1.1 可复现 machine 位置/速度
- 若 addresses count 不是 16，耐心追 cause ；可能是 build config/optimizer 改变了编译 layout
- 1.05 newer progression 也许会把 `_` format 转为 dot format，请写 storage backup

## H. 未来版本指南（如果出现 newer update）

1. 先算 PPU hash。
2. 跑 emulator 在 stable anchor 验证 load。
3. 对 EMAIN scan float。
4. 与 latest candidate address set 做 diff，确认哪些 segment shifts。
5. 直接用 same 16 常量 route 或 proof by runtime patch。
6. 测试 3D ratio + HUD coordinate behavior。

## I. 参考证据

请把以下证据和 commit 一起放 repo：

- 驾驶学校 1.1 相同机位 screenshots
- no-patch baseline `00b-*`
- `_stage0_backup_` snapshot
- `ppuhash.py` output
- log snippets

---

MIT  Attribution: gt6-uw (moon) on 2026-10-28