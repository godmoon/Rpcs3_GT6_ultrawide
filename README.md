# Gran Turismo 6 RPCS3 Ultrawide 32:9

面向 RPCS3 上 **Gran Turismo 6 (BCAS25018)** 的真正 32:9 超宽屏补丁，不是简单的画面拉伸。

## 目标

- 显示/输出尺寸：`2560 × 720`
- 显示比例：32:9
- 游戏内部 3D 按 32:9 渲染
- 水平 FOV 真正变大
- 3D 比例保持正常，而不是把 16:9 内容横拉

## 工作原理

GT6 内部多处使用 `1.7777778f` 作为 16:9 长宽比常量。本补丁把其中 **16 个** 编译期常量从：

```text
1.7777778 -> 3.5555556
```

渲染理解为：

```text
GT6 内部按 32:9 3D FOV/近远/aspect 进行渲染
  -> RPCS3 渲染面
  -> GPU -> Stretch To Display Area
  -> 2560 x 720 输出
```

## 已验证版本

| 版本 | PPU hash |
| --- | --- |
| 1.00 | `PPU-dd7ec6f4719ae9938b2e76bed97232ffc9dbdda1` |
| 1.05 | `PPU-824c9dd3c8f7de8b5060ec99b06f474de274de35` |

说明：
- 两个版本的 `EMAIN.SELF` 常量坐标不同。
- 必须按运行的 `EMAIN` hash 选 patch，不能直接复用地址。
- patch 不能“通用地”写死在所有版本上，需要 port。

## 仓库目录

```text
gt6-rpcs3-ultrawide/
  README.md
  USAGE.md
  PATCH_BUILD_GUIDE.md
  patch_config.example.yml
  patches/
    BCAS25018_patch.yml
  legacy/
    BCAS25018-32x9-test.yml
  tools/
    ...
```

## 使用前要求

- 每次只启用 **一个** patch。
- 切换 patch 前，必须完全退出游戏再重新启动 RPCS3。
- `Stretch To Display Area` 应当开启。
- 推荐使用固定机位截图对比，不建议以完整比赛作为验证证据。

## 已知限制

- 1.00 有已知 game-breaking bug。
- 1.05 不能跑全部 progression（需要视 save 生成而定）。
- HUD/2D 坐标可能需要单独 patch，当前以 3D horizontal FOV 为主。

## 文档

- `USAGE.md`：安装、设置、使用和故障排除
- `PATCH_BUILD_GUIDE.md`：从新版本 ELF 提取新 patch 的流程
- ` patch_config.example.yml`：UI/配置选项示例
- `legacy/BCAS25018-32x9-test.yml`：实验数据和过渡证据

---

MIT License. Attribution: gt6-uw (moon), 2026-10-28