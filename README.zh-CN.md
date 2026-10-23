# Awesome XGO-Duck [![非官方](https://img.shields.io/badge/%E7%8A%B6%E6%80%81-%E9%9D%9E%E5%AE%98%E6%96%B9-orange)](#关于这份合集)

[English](README.md) · **简体中文**

> [!IMPORTANT]
> **这是一份非官方的社区合集。** 它不是陆吾智能（Luwu Dynamics）、Pollen Robotics 或 Arduino 制作、认可或审核的。官方文件、更新和支持请看[官方仓库](#官方)。

收集 [XGO-Duck](https://github.com/LuwuDynamics/xgoduck_hardware) 的策略（训练好的模型）、打印件、工具和教程。XGO-Duck 是一只基于 Arduino® UNO Q 和 15 个总线舵机的鸭形双足机器人。

- [官方](#官方)
- [策略](#策略)
- [3D 打印](#3d-打印)
- [工具](#工具)
- [训练](#训练)
- [视频](#视频)
- [上游与致谢](#上游与致谢)
- [参与贡献](#参与贡献)
- [关于这份合集](#关于这份合集)

## 官方

- [xgoduck_hardware](https://github.com/LuwuDynamics/xgoduck_hardware)：可打印结构（STL）、扩展板、物料清单。维护者说明这一版硬件仅用于学习和测试。
  - [装配指南（PDF）](https://github.com/LuwuDynamics/xgoduck_hardware/blob/HEAD/Assembly_Guide.pdf) · [打印](https://github.com/LuwuDynamics/xgoduck_hardware/blob/HEAD/docs/PRINTING.md) · [制作指南](https://github.com/LuwuDynamics/xgoduck_hardware/blob/HEAD/docs/BUILD_GUIDE.md) · [常见问题](https://github.com/LuwuDynamics/xgoduck_hardware/blob/HEAD/docs/FAQ.md) · [故障排查](https://github.com/LuwuDynamics/xgoduck_hardware/blob/HEAD/docs/TROUBLESHOOTING.md)
- [XGO-Duck 产品页](https://www.xgorobot.com/duck.html)：陆吾智能官网，可以买电子套件，也可以下载官方桌面配置工具 **Duck Setup**（macOS、Windows、Linux）。
- [MakerWorld 上的 XGO-Duck](https://makerworld.com.cn/zh/models/3098881-xgo-duck-da-zao-shu-yu-ni-de-shuang-zu-ji-qi-ya)：陆吾智能官方页面，有打印配置、物料清单、舵机参数和制作步骤。
- [xgoduck_runtime_arduino](https://github.com/LuwuDynamics/xgoduck_runtime_arduino)：在机器人上运行的 Arduino App。Linux 以 50 Hz 运行 ONNX 策略，STM32 以 100 Hz 驱动舵机和 IMU，网页控制台在 9527 端口。
- [xgoduck_rl](https://github.com/LuwuDynamics/xgoduck_rl)：训练环境（mjlab、PPO）和 ONNX 导出。
- [Discord](https://discord.com/invite/pfWrJeJRh6)：官方 README 里给出的社区服务器。

## 策略

别人训练好的模型，可以替换运行时自带的模型。文件留在作者发布的地方，[`policies/index.yaml`](policies/index.yaml) 只列出它们和校验和。

<!-- policies:start -->
| 策略 | 替换 | 作者 | 许可 | 说明 |
| --- | --- | --- | --- | --- |
| [行走 · 2026-09-22 版运行时](https://github.com/LuwuDynamics/xgoduck_runtime_arduino/tree/5f1954aff0df12733b69bc8405fac177a4cd9c60) | XGO-Duck · 行走 | Luwu Dynamics | 未声明 | 官方运行时从首个版本到 2026-10-22 之前自带的行走模型。 |
| [行走 · 2026-10-22 版运行时](https://github.com/LuwuDynamics/xgoduck_runtime_arduino/tree/466512e9426f61fb07d9be9b3f20df0171692150) | XGO-Duck · 行走 | Luwu Dynamics | 未声明 | 运行时 466512e 更新的行走模型，截至 2026-10-23 仍是原版自带的行走模型。 |
<!-- policies:end -->

**用 [Quay](https://github.com/caoxg/quay) 安装：** 在 App 卡片上点「策略」，再点「安装」。也可以在终端里运行：

```bash
quay policy install xgoduck_runtime_arduino walk-luwu-2026-09-22
```

Quay 会做这些事：

- 校验 SHA-256；
- 检查模型和插槽是否匹配（输入 `[1,61]`、输出 `[1,14]`、关节顺序一致）；
- 保留原版模型；
- 如果换上后机器人启动失败，自动换回之前的模型；
- 每次更新运行时后，重新放回你选的模型。

**手动安装：**

1. 下载文件，对照索引核对 SHA-256。
2. 备份原来的文件。
3. 用下载的文件覆盖板子上 `~/ArduinoApps/<App 文件夹>/python/` 里对应插槽的文件。
4. 重启 App。

注意：更新运行时会把原版文件放回去。

| 插槽 | `python/` 里的文件 | 用途 |
| --- | --- | --- |
| `walk` | `xgoduck_walk.onnx` | 行走（默认），也用于摔倒恢复后的行走 |
| `roller` | `xgoduck_roller.onnx` | 轮滑模式，需要装上轮滑套件（见 [3D 打印](#3d-打印)）；初始姿态取自模型的 `default_joint_pos` |
| `getup` | `xgoduck_getup.onnx` | 摔倒后起身 |
| `pick` | `xgoduck_pick.onnx` | 4 秒的啄食动作 |
| `roulade` | `xgoduck_roulade.onnx` | 1.9 秒的翻滚 |

训练了自己的模型？看[如何发布策略](policies/README.md)。

## 3D 打印

- [MakerWorld 官方打印配置](https://makerworld.com.cn/zh/models/3098881-xgo-duck-da-zao-shu-yu-ni-de-shuang-zu-ji-qi-ya)，陆吾智能发布：
  - 整机：6 盘，约 16 小时；H2 系列打印机是 4 盘；
  - **轮滑套件**（轮滑模式要用）：1 盘，约 1.5 小时。

  请按页面要求摆放：零件平躺、凹槽朝上，4 层墙、13% 螺旋填充。许可是 MakerWorld 独家许可：改版只能发在 MakerWorld，要注明陆吾智能，不能商用。
- GitHub 上的[官方 STL 文件](https://github.com/LuwuDynamics/xgoduck_hardware/tree/HEAD/structure)和[打印说明](https://github.com/LuwuDynamics/xgoduck_hardware/blob/HEAD/docs/PRINTING.md)（TPU 脚底、摆放方向、材料）。
- **标定（舵机中位校准）：**
  - [xgoduck中位校准托盘](https://makerworld.com.cn/zh/models/3136258-xgoduckzhong-wei-xiao-zhun-tuo-pan)，作者「星猫」，发布在 MakerWorld。
    - 用法：鸭子卸力后，背朝下放进托盘，头、身体和双脚都对准托座，托盘会把它固定在中位姿态，再逐个关节点「Set center & hold」。做动作测试前先取出来。
    - 打印：PETG，需要约 244 × 244 mm 的打印平台，A1 mini 放不下。
    - 许可：CC BY-NC-SA 4.0。
  - 中位就是策略里每个关节 0° 时的姿态：腿竖直向下，脚放平、脚尖朝前，脖子竖直，头平视前方，嘴闭合。中位偏了，在 Default pose 里就会表现为身体前倾或后仰。
- **切片配置和改版：** 请链接到你发布的地方，并写明许可。
  - 官方零件的改版请发在 MakerWorld，因为官方页面的许可只允许在那里发布衍生作品；
  - GitHub 上的文件目前还没有许可证（见 [LICENSING.md](https://github.com/LuwuDynamics/xgoduck_hardware/blob/HEAD/LICENSING.md)）；
  - 你自己的设计（比如上面的标定托盘）用什么许可由你决定。

## 工具

- [Quay](https://github.com/caoxg/quay)（非官方）：UNO Q App 的桌面应用和命令行工具。可以：
  - 从 git 安装、更新运行时，并保留 `data/`；
  - 一键安装这份合集里的策略；
  - 切换国内镜像；
  - 不经 App Lab 做系统更新。

## 训练

- [xgoduck_rl](https://github.com/LuwuDynamics/xgoduck_rl)：`uv run list-envs` 会列出所有任务，例如 `Mjlab-Velocity-Flat-XgoDuck` 和 `Mjlab-Velocity-Swizzle-XgoDuck`（轮滑）。训练需要 CUDA 显卡。
- 分享导出的模型前，运行 `quay policy inspect model.onnx --app xgoduck`，可以查看形状和元数据，并生成一条索引条目。

## 视频

### 哔哩哔哩

- [XGO-Duck 组装教程｜一只机器鸭的诞生](https://www.bilibili.com/video/BV1h1Ww6XE3m/)：陆吾智能官方，23 分钟，完整组装过程。
- [陆吾智能联合飞特舵机推出全新开源项目 XGO-Duck](https://www.bilibili.com/video/BV15Ta562E5e/)：飞特舵机工厂，1 分钟，演示行走、跌倒起身、用鸭嘴夹东西。

### YouTube

- [How to Build XGO-Duck | Robot Assembly Tutorial](https://www.youtube.com/watch?v=nElGguHO5dY)：CyberBionic Maker，陆吾智能的频道。
- [Meet XGO-Duck | A Robot You Can Build, Code & Explore](https://www.youtube.com/watch?v=tiDCkt-TwWM)：CyberBionic Maker。
- [XGO-Duck刚刚开源！Microduck最有力平替](https://www.youtube.com/watch?v=zWF2MOS6fJM)：轻松易学嵌入式，中文介绍。
- [xgo duck unified demo](https://www.youtube.com/watch?v=-6R_79_7PM0)：Jairo Bambang Oetomo，玩家实机演示。

### 小红书

还没有收录。欢迎发来你的笔记链接（`xhslink.com/…` 或 `xiaohongshu.com/explore/…`）。

### 上游：Microduck

- [Meet Microduck](https://www.youtube.com/watch?v=reiTh7K4KSc) 和 [Microduck Sim 2 Real](https://www.youtube.com/watch?v=szW7N_7B3tU)：Pollen Robotics 官方。XGO-Duck 改编自这只机器人；第二个视频讲策略怎样从仿真迁移到真机。
- [Getting Started Training a Walking RL PPO Policy with Mjlab](https://www.youtube.com/watch?v=ZDvCdIFXANw)：Kevin Wood。用 mjlab 训练行走策略，xgoduck_rl 用的就是这个框架。

## 上游与致谢

XGO-Duck 是陆吾智能基于 Pollen Robotics 的 [Microduck](https://pollen-robotics.com/microduck/)（[运行时](https://github.com/pollen-robotics/microduck)、[microduck_rl](https://github.com/pollen-robotics/microduck_rl)）做的适配。训练使用 [mjlab](https://github.com/mujocolab/mjlab)，执行器模型来自 Rhoban 的 [BAM](https://github.com/Rhoban/bam)。详见官方的[来源说明](https://github.com/LuwuDynamics/xgoduck_hardware/blob/HEAD/UPSTREAM.md)。

## 参与贡献

欢迎提 Pull Request，每个 PR 请只加一项。

- **加链接**（切片配置、视频、文章、工具）：同时加到 `README.md` 和 `README.zh-CN.md`，各附一句说明。视频放在对应平台下面，写上原标题和作者。
- **加策略**：按 [policies/README.md](policies/README.md) 操作，然后运行 `uv run tools/index.py check`。每个 PR 也会自动跑这项检查。
- 只分享你有权分享的内容，并写明许可。这个仓库只放链接，不存放模型或设计文件。

## 关于这份合集

由 [@caoxg](https://github.com/caoxg) 和贡献者维护，独立于陆吾智能。收录不代表保证兼容：新策略请先在支架上测试，手放在「Torque off」附近。

XGO 和 XGO-Duck 是陆吾智能使用的名称；Arduino® 和 UNO® 是 Arduino SA 的商标。这里使用这些名称，只是为了说明所列内容的用途。

合集文字以 [CC0 1.0](LICENSE) 发布；所列作品各自保留其许可。
