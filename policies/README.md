# Publishing a policy · 发布策略

[`index.yaml`](index.yaml) lists XGO-Duck policies that other people can install. The model files stay with their authors; this repository holds only the list.
[`index.yaml`](index.yaml) 列出了大家可以安装的 XGO-Duck 策略。模型文件由作者自己托管，这个仓库只存放列表。

## Steps · 步骤

1. **Check the export on a real duck.** Test it on a stand first, with a hand near *Torque off*.
   **先在真机上验证导出的模型。** 先在支架上测试，手放在「Torque off」附近。
2. **Put the `.onnx` file somewhere stable.** We suggest doing both:
   - Attach it to a **GitHub release** of your own repository, and use that link as `url`. Its download count is then public.
   - Commit the same file to the repository too, and put its **jsDelivr** link in `mirrors` for readers in China. jsDelivr serves files in a repository, not release attachments. Pin the release's tag or a commit, never a branch: `https://cdn.jsdelivr.net/gh/you/your-repo@v1/model.onnx`.

   Keep published URLs unchanged; publish a new version under new URLs.

   **把 `.onnx` 文件放在稳定的位置。** 建议两种方式都用：
   - 把它作为附件发到你自己仓库的 **GitHub Release**，用这个地址作 `url`，这样下载次数是公开的。
   - 同时把同一个文件提交进仓库，把它的 **jsDelivr** 地址填进 `mirrors`，方便国内用户下载。jsDelivr 只镜像仓库里的文件，不镜像 Release 附件。地址里写死 Release 的标签或 commit，不要用分支名：`https://cdn.jsdelivr.net/gh/you/your-repo@v1/model.onnx`。

   不要改动已发布的网址；新版本请用新网址。
3. **Generate the entry:**
   **生成条目：**
   ```bash
   quay policy inspect model.onnx --app xgoduck --url https://github.com/you/your-repo/releases/download/v1/model.onnx
   ```
   It prints the shapes, the metadata, the SHA-256, the size, and an entry to fill in.
   它会打印形状、元数据、SHA-256、大小，以及一条待填写的条目。
4. **Add the entry** to `index.yaml` (newest last), with your `mirrors` link from step 2; `quay policy inspect` doesn't print one. Run `uv run tools/index.py table`, then `uv run tools/index.py check`, and open a pull request.
   **把条目加到** `index.yaml` 末尾，并加上第 2 步的 `mirrors` 地址（`quay policy inspect` 不会打印这一项）。运行 `uv run tools/index.py table` 和 `uv run tools/index.py check`，然后提 Pull Request。

## Fields · 字段

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Unique, lowercase: `a-z 0-9 . - _`, e.g. `walk-smooth-alice-v1` |
| `app` | yes | `xgoduck` |
| `slot` | yes | `walk`, `roller`, `getup`, `pick` or `roulade` (see the [slot table](../README.md#policies)) |
| `name`, `name_zh` | `name` | Display name (English, Chinese) |
| `author` | yes | Your name or GitHub handle |
| `description`, `description_zh` | recommended | What it does differently from the stock model, and how you tested it on hardware |
| `url` | yes | `https://` link to the file |
| `mirrors` | no | Other `https://` links to the same file, e.g. jsDelivr for readers in China |
| `sha256`, `size` | yes | From `quay policy inspect` |
| `license` | yes | e.g. `Apache-2.0`, `CC-BY-4.0` |
| `trainer` | recommended | Training code and revision, e.g. `LuwuDynamics/xgoduck_rl afd091b, Mjlab-Velocity-Flat-XgoDuck` |
| `homepage`, `video` | recommended | Model card or repository; a continuous real-time clip of it running |
| `created` | recommended | `YYYY-MM-DD` |

## What the check verifies · 检查内容

`tools/index.py check` runs on every pull request. It checks the fields, downloads each file, compares the SHA-256 and the size, and loads the model with ONNX:

- input `[1,61]` and output `[1,14]`;
- `joint_names` and `observation_names` metadata equal to the runtime's order;
- for `roller`, a `default_joint_pos` with 14 finite numbers.

Quay runs the same checks again before installing, against the stock model on the board.

`tools/index.py check` 在每个 Pull Request 上运行。它会检查字段，下载每个文件，核对 SHA-256 和大小，并用 ONNX 加载模型：

- 输入 `[1,61]`、输出 `[1,14]`；
- `joint_names`、`observation_names` 元数据和运行时的顺序一致；
- `roller` 插槽还要有 14 个有限数值的 `default_joint_pos`。

Quay 在安装前还会对照板子上的原版模型再检查一遍。

Passing the check means the model fits the slot. It does not mean the model walks well. The description and the video tell people that.
通过检查只说明模型和插槽匹配，不代表它走得好。走得好不好，要靠说明和视频来展示。

## Rules · 规则

- Share only models you have the right to share, and state the license.
  只分享你有权分享的模型，并写明许可。
- Don't include personal data in the metadata. `run_path` often contains a local path.
  元数据里不要带个人信息。`run_path` 里常常有本机路径。
- An entry may be removed if its file disappears or changes (the checksum stops matching).
  如果条目的文件消失或被改动（校验和对不上），条目可能会被删除。
