# Awesome XGO-Duck [![Unofficial](https://img.shields.io/badge/status-unofficial-orange)](#about-this-list)

**English** · [简体中文](README.zh-CN.md)

> [!IMPORTANT]
> **This is an unofficial, community-maintained collection.** It is not made, endorsed or checked by Luwu Dynamics (陆吾智能), Pollen Robotics or Arduino. For official files, updates and support, use the [official repositories](#official).

Policies (trained models), printable parts, tools and guides for [XGO-Duck](https://github.com/LuwuDynamics/xgoduck_hardware), the duck-shaped biped robot built on an Arduino® UNO Q with 15 bus servos.

- [Official](#official)
- [Policies](#policies)
- [3D printing](#3d-printing)
- [Tools](#tools)
- [Training](#training)
- [Videos](#videos)
- [Upstream and credits](#upstream-and-credits)
- [Contributing](#contributing)
- [About this list](#about-this-list)

## Official

- [xgoduck_hardware](https://github.com/LuwuDynamics/xgoduck_hardware) — printable structure (STL), expansion board, BOM. The maintainer marks this hardware revision as for learning and testing only.
  - [Assembly guide (PDF)](https://github.com/LuwuDynamics/xgoduck_hardware/blob/HEAD/Assembly_Guide.pdf) · [Printing](https://github.com/LuwuDynamics/xgoduck_hardware/blob/HEAD/docs/PRINTING.md) · [Build guide](https://github.com/LuwuDynamics/xgoduck_hardware/blob/HEAD/docs/BUILD_GUIDE.md) · [FAQ](https://github.com/LuwuDynamics/xgoduck_hardware/blob/HEAD/docs/FAQ.md) · [Troubleshooting](https://github.com/LuwuDynamics/xgoduck_hardware/blob/HEAD/docs/TROUBLESHOOTING.md)
- [XGO-Duck product page](https://www.xgorobot.com/duck.html) — Luwu Dynamics' site, in Chinese: the electronics kit, and downloads of **Duck Setup**, their desktop setup tool for macOS, Windows and Linux.
  - **Join the WeChat group.** On the product page, *入群咨询交流* shows the QR code of the official WeCom (企业微信) group, where Luwu takes questions before you buy, usage problems and technical discussion. The official WeChat account there only handles payment and shipping. If adding it fails, join the group first and add “陆吾智能LuwuDynamics” from there.
- [XGO-Duck on MakerWorld](https://makerworld.com.cn/zh/models/3098881-xgo-duck-da-zao-shu-yu-ni-de-shuang-zu-ji-qi-ya) — Luwu Dynamics' own page, in Chinese: print profiles, hardware list, servo specifications, build steps.
- [xgoduck_runtime_arduino](https://github.com/LuwuDynamics/xgoduck_runtime_arduino) — the Arduino App that runs on the robot: ONNX policies at 50 Hz on Linux, the STM32 drives the servos and the IMU at 100 Hz, web console on port 9527.
- [xgoduck_rl](https://github.com/LuwuDynamics/xgoduck_rl) — training environments (mjlab, PPO) and ONNX export.
- [Discord](https://discord.com/invite/pfWrJeJRh6) — the community server linked from the official README.

## Policies

Models other people trained, to swap into the runtime in place of the stock ones. The files stay where their authors publish them; [`policies/index.yaml`](policies/index.yaml) lists them with their checksums.

<!-- policies:start -->
| Policy | Replaces | Author | License | Notes |
| --- | --- | --- | --- | --- |
| [Walk · runtime of 2026-09-22](https://github.com/LuwuDynamics/xgoduck_runtime_arduino/tree/5f1954aff0df12733b69bc8405fac177a4cd9c60) | XGO-Duck · Walk | Luwu Dynamics | not stated | The walking model the official runtime shipped from its first release until 2026-10-22. |
| [Walk · runtime of 2026-10-22](https://github.com/LuwuDynamics/xgoduck_runtime_arduino/tree/466512e9426f61fb07d9be9b3f20df0171692150) | XGO-Duck · Walk | Luwu Dynamics | not stated | The "updated walking policy" of runtime 466512e, still the stock walk as of 2026-10-23. |
<!-- policies:end -->

**Install with [Quay](https://github.com/caoxg/quay):** on the app card, choose *Policies*, then *Install*. Or, from a terminal:

```bash
quay policy install xgoduck_runtime_arduino walk-luwu-2026-09-22
```

Quay checks the SHA-256 and that the model fits the slot (input `[1,61]`, output `[1,14]`, same joint order), keeps the stock model, puts the previous model back if the robot does not start with the new one, and re-applies your choice after every runtime update.

**Install by hand:** download the file, compare its SHA-256 with the index, keep a copy of the original, and copy the file over the slot's file in `~/ArduinoApps/<app folder>/python/` on the board. Then restart the app. Updating the runtime puts the stock file back.

| Slot | File in `python/` | Used for |
| --- | --- | --- |
| `walk` | `xgoduck_walk.onnx` | walking (the default) and the recovery walk |
| `roller` | `xgoduck_roller.onnx` | Roller mode, with the roller kit fitted ([3D printing](#3d-printing)). Its home pose comes from the model's `default_joint_pos` |
| `getup` | `xgoduck_getup.onnx` | getting up after a fall |
| `pick` | `xgoduck_pick.onnx` | the 4 s pick move |
| `roulade` | `xgoduck_roulade.onnx` | the 1.9 s roulade |

Trained one? See [publishing a policy](policies/README.md).

## 3D printing

- [Official print profiles on MakerWorld](https://makerworld.com.cn/zh/models/3098881-xgo-duck-da-zao-shu-yu-ni-de-shuang-zu-ji-qi-ya), by Luwu Dynamics:
  - the whole robot: 6 plates, about 16 h, or 4 plates on H2 printers;
  - the **roller kit** that *Roller mode* needs: 1 plate, about 1.5 h.

  Follow the page's orientation note: parts lie flat with their grooves open upward, 4 walls, 13 % gyroid infill. It is under the MakerWorld Exclusive License: remixes may be published only on MakerWorld, crediting Luwu Dynamics, and not used commercially.
- [Official STL files](https://github.com/LuwuDynamics/xgoduck_hardware/tree/HEAD/structure) and [printing notes](https://github.com/LuwuDynamics/xgoduck_hardware/blob/HEAD/docs/PRINTING.md) on GitHub (TPU feet, orientation, material).
- **Calibration** (setting each servo's center):
  - [xgoduck中位校准托盘](https://makerworld.com.cn/zh/models/3136258-xgoduckzhong-wei-xiao-zhun-tuo-pan) (center calibration tray) by 星猫, on MakerWorld. With torque off, lay the duck on its back in the tray, with the head, body and both feet in their seats. It then holds the center pose while you press *Set center & hold* for each joint. Take the duck out before motion tests. Print in PETG; it needs a bed of about 244 × 244 mm, so the A1 mini is too small. CC BY-NC-SA 4.0.
  - The center is the pose the policies call 0° for every joint: legs straight down with the feet flat and pointing forward, the neck upright, the head level and facing forward, the beak closed. An offset here shows up as a lean in *Default pose*.
- **Print profiles and remixes:** link to where you publish them and state the license.
  - A remix of the official parts goes on MakerWorld, because the official page's license allows derivatives only there.
  - The GitHub files have no license yet ([LICENSING.md](https://github.com/LuwuDynamics/xgoduck_hardware/blob/HEAD/LICENSING.md)).
  - Your own designs, such as the calibration tray above, carry whatever license you choose.

## Tools

- [Quay](https://github.com/caoxg/quay) (unofficial) — desktop app and CLI for UNO Q apps: install and update the runtime from git while keeping its `data/`, one-click policies from this list, China mirrors, and system updates without App Lab.

## Training

- [xgoduck_rl](https://github.com/LuwuDynamics/xgoduck_rl): `uv run list-envs` lists the tasks, e.g. `Mjlab-Velocity-Flat-XgoDuck` and `Mjlab-Velocity-Swizzle-XgoDuck` (the roller walk). It needs a CUDA GPU.
- Before you share an export, `quay policy inspect model.onnx --app xgoduck` shows its shapes and metadata and prints an index entry.

## Videos

### Bilibili

- [XGO-Duck 组装教程｜一只机器鸭的诞生](https://www.bilibili.com/video/BV1h1Ww6XE3m/) — Luwu Dynamics (official), 23 min. The whole assembly, in Chinese.
- [陆吾智能联合飞特舵机推出全新开源项目 XGO-Duck](https://www.bilibili.com/video/BV15Ta562E5e/) — Feetech's servo factory, 1 min. Walking, getting up, picking with the beak.

### YouTube

- [How to Build XGO-Duck | Robot Assembly Tutorial](https://www.youtube.com/watch?v=nElGguHO5dY) — CyberBionic Maker, Luwu Dynamics' channel.
- [Meet XGO-Duck | A Robot You Can Build, Code & Explore](https://www.youtube.com/watch?v=tiDCkt-TwWM) — CyberBionic Maker.
- [XGO-Duck刚刚开源！Microduck最有力平替](https://www.youtube.com/watch?v=zWF2MOS6fJM) — 轻松易学嵌入式. An introduction in Chinese.
- [xgo duck unified demo](https://www.youtube.com/watch?v=-6R_79_7PM0) — Jairo Bambang Oetomo. A builder's demo.

### Xiaohongshu (小红书)

Nothing listed yet. Send the link to your note (`xhslink.com/…` or `xiaohongshu.com/explore/…`).

### Upstream: Microduck

- [Meet Microduck](https://www.youtube.com/watch?v=reiTh7K4KSc) and [Microduck Sim 2 Real](https://www.youtube.com/watch?v=szW7N_7B3tU) — Pollen Robotics. The robot XGO-Duck adapts, and how its policies move from simulation to the real robot.
- [Getting Started Training a Walking RL PPO Policy with Mjlab](https://www.youtube.com/watch?v=ZDvCdIFXANw) — Kevin Wood. Training with mjlab, the framework xgoduck_rl uses.

## Upstream and credits

XGO-Duck is Luwu Dynamics' adaptation of [Microduck](https://pollen-robotics.com/microduck/) by Pollen Robotics ([runtime](https://github.com/pollen-robotics/microduck), [microduck_rl](https://github.com/pollen-robotics/microduck_rl)). Training uses [mjlab](https://github.com/mujocolab/mjlab), and actuator models come from [BAM](https://github.com/Rhoban/bam) by Rhoban. See the official [origins page](https://github.com/LuwuDynamics/xgoduck_hardware/blob/HEAD/UPSTREAM.md).

## Contributing

Pull requests are welcome. One addition per pull request, please.

- **A link** (print profile, video, article, tool): add it to both `README.md` and `README.zh-CN.md`, with a one-line description. A video goes under its platform, with its title as published and the channel.
- **A policy:** follow [policies/README.md](policies/README.md), then run `uv run tools/index.py check`. The check also runs on every pull request.
- Share only material you have the right to share, and say under which license. This repository holds no model or design files, only links.

## About this list

Maintained by [@caoxg](https://github.com/caoxg) and contributors. It is independent of Luwu Dynamics. Listing something here is not a compatibility guarantee: test new policies on a stand first, with a hand near *Torque off*.

XGO and XGO-Duck are names of Luwu Dynamics. Arduino® and UNO® are trademarks of Arduino SA. Names are used only to say what the listed work is for.

The text of this list is released under [CC0 1.0](LICENSE). Each listed work keeps its own license.
