# Usage

## 1. 环境

- RPCS3 官方版本（建议最新 stable）
- PS3 GT6 `BCAS25018`
- `01.00`（含对应 hash）或 `01.05`
- Windows / Linux（Mac 未验证）

## 2. 安装补丁

1. 把 `patches/BCAS25018_patch.yml` 复制到 RPCS3 的 `patches/` 目录。
2. 启动 RPCS3，左侧面板选中 BCAS25018，右键：
   - Manage Game Patches
3. 只勾选一个：
   - 1.00：`32:9 UWW (GT6 1.00, all 16)`
   - 1.05：`32:9 UWW (GT6 1.05, 16 constants)`
4. 完全退出 RPCS3，重新启动，再运行游戏。

说明：
- 文件名必须是 `BCAS25018_patch.yml`，RPCS3 只加载这个文件名。
- 若你已打开 Manage Game Patches，勾选后仍无反应，请重启 RPCS3。

## 3. 推荐 RPCS3 设置

| 项目 | 建议值 |
| --- | --- |
| Renderer | Vulkan |
| Resolution | 2560 x 720（优先），或 1280 x 720 + Stretch |
| GPU: Stretch To Display Area | 启用 |
| SPU Block Size | Mega |
| Accurate RSX reservation access | 启用 |
| RSX FIFO Accuracy | Atomic |
| 全屏 | 先非全屏，便于固定窗口和截图 |

## 4. 使用流程

- 进入 GT6，打开驾驶学校 / 计时赛 / 自由跑
- 用同一机位、同一时间点做 before/after 截图
- 先跑 baseline（无 patch + Stretch），再跑 patched
- 不要在测试期间跑完整比赛
- patch 切换必须完全退出

固定机位建议：
- 驾驶学校 1.1（Brands Hatch）
- 暂停 → 重新開始，车回起点 `0 km/h`

## 5. 存档说明

- 主存档：`dev_hdd0/home/00000001/savedata/BCJS37016-GAME6`
- 备份槽：`dev_hdd0/home/00000001/savedata/BCJS37016-BKUP6`
- 若切回 1.00 后再次询问姓名，说明 1.00 没找到 dot format save：
  1. 先把 1.05 恢复为 active 目录
  2. 用 1.05 读取并覆盖保存一次
  3. 再切回 1.00

## 6. 部署回滚

### 回滚 patch

- `patch_config.yml` 还原为 `{}`：关闭所有 patch
- 删除 `BCAS25018_patch.yml`：完全移除 patch 入口

### 回滚 game 目录

- `dev_hdd0/game/BCAS25018` → `BCAS25018.105-off`
- `dev_hdd0/game/BCAS25018.100-off` → `BCAS25018`

### 回滚游戏资料

- 恢复先前 `savedata` 备份
- `BCAS25018.100-off / .105-off` 可一键还原

## 7. 故障排除

| 问题 | 处理 |
| --- | --- |
| Manage Game Patches 里没有 UWW | 确认文件名为 `BCAS25018_patch.yml`；重启 RPCS3 |
| 勾选后画面无变化 | 确认 only one patch；确认 `Stretch To Display Area` 已启；重新启动游戏 |
| 1.00 载入 save 后询问姓名 | 先在 1.05 下打开并覆盖保存，再切回 1.00 |
| patch 只在 Manage Patches 使用 | 重启 RPCS3 以确保 loader 重新读取补丁文件 |
| 画面比例仍不对 | 检查窗口/渲染面是否为 2560x720（或等价 32:9） |

## 8. 快速检查

日志中应出现：

```text
PPU executable hash: PPU-dd7ec...   (1.00)
PPU executable hash: PPU-824c...    (1.05)
```