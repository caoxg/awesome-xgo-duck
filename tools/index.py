# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6", "onnx>=1.16"]
# ///
"""Checks policies/index.yaml and keeps the policy tables in the READMEs in step with it.

    uv run tools/index.py check            # schema, download (mirrors too), SHA-256, size, ONNX shapes and metadata
    uv run tools/index.py check --offline  # schema and README tables only
    uv run tools/index.py table            # rewrite the tables in README.md and README.zh-CN.md
"""
from __future__ import annotations

import argparse
import hashlib
import math
import pathlib
import re
import sys
import urllib.request

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "policies" / "index.yaml"
READMES = {"en": ROOT / "README.md", "zh": ROOT / "README.zh-CN.md"}
CACHE = pathlib.Path.home() / ".cache" / "awesome-xgo-duck"
MAX_SIZE = 256 << 20

# What each app's runtime loads (mirrors the slots in Quay's built-in profile for the app).
JOINTS = ("left_hip_yaw,left_hip_roll,left_hip_pitch,left_knee,left_ankle,neck_pitch,head_pitch,head_yaw,"
          "head_roll,right_hip_yaw,right_hip_roll,right_hip_pitch,right_knee,right_ankle")
APPS = {
    "xgoduck": {
        "name": {"en": "XGO-Duck", "zh": "XGO-Duck"},
        "input": [1, 61],
        "output": [1, 14],
        "match": {
            "joint_names": JOINTS,
            "observation_names": "base_ang_vel,projected_gravity,joint_pos,joint_vel,actions,command,head_command,body_command",
        },
        "slots": {
            "walk": {"en": "Walk", "zh": "行走", "require": []},
            "roller": {"en": "Roller walk", "zh": "轮滑", "require": ["default_joint_pos"]},
            "getup": {"en": "Get up", "zh": "起身", "require": []},
            "pick": {"en": "Pick", "zh": "啄食", "require": []},
            "roulade": {"en": "Roulade", "zh": "翻滚", "require": []},
        },
    },
}
REQUIRED = ("id", "app", "slot", "name", "author", "url", "sha256", "size", "license")
KNOWN = set(REQUIRED) | {"name_zh", "description", "description_zh", "mirrors", "trainer", "homepage", "video", "created"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


def load() -> dict:
    with INDEX.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_schema(ix: dict) -> list[str]:
    errs = []
    if ix.get("version") != 1:
        errs.append("version must be 1")
    seen = set()
    for i, e in enumerate(ix.get("policies") or []):
        where = f"entry {i + 1} ({e.get('id', '?')})"
        for k in REQUIRED:
            if e.get(k) in (None, ""):
                errs.append(f"{where}: {k} is required")
        for k in e:
            if k not in KNOWN:
                errs.append(f"{where}: unknown field {k}")
        if not ID_RE.match(str(e.get("id", ""))) or e.get("id") in seen:
            errs.append(f"{where}: id must be unique and use a-z, 0-9, '.', '-' or '_'")
        seen.add(e.get("id"))
        app = APPS.get(e.get("app"))
        if not app:
            errs.append(f"{where}: unknown app {e.get('app')!r} (known: {', '.join(APPS)})")
        elif e.get("slot") not in app["slots"]:
            errs.append(f"{where}: unknown slot {e.get('slot')!r} (slots: {', '.join(app['slots'])})")
        if not re.fullmatch(r"[0-9a-f]{64}", str(e.get("sha256", ""))):
            errs.append(f"{where}: sha256 must be 64 lowercase hex digits")
        if not isinstance(e.get("size"), int) or not 0 < e["size"] <= MAX_SIZE:
            errs.append(f"{where}: size must be the file size in bytes")
        for u in [e.get("url")] + list(e.get("mirrors") or []):
            if not str(u).startswith("https://"):
                errs.append(f"{where}: {u!r} is not an https URL")
        if e.get("created") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(e["created"])):
            errs.append(f"{where}: created must be YYYY-MM-DD")
    return errs


def fetch(url: str, size: int) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "awesome-xgo-duck-index-check"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(size + 1)


def check_model(e: dict, data: bytes) -> list[str]:
    import onnx

    app = APPS[e["app"]]
    errs = []
    try:
        m = onnx.load_model_from_string(data)
    except Exception as ex:  # noqa: BLE001
        return [f"not an ONNX model: {ex}"]
    weights = {t.name for t in m.graph.initializer}
    inputs = [i for i in m.graph.input if i.name not in weights]

    def shape(v):
        return [d.dim_value if d.HasField("dim_value") else -1 for d in v.type.tensor_type.shape.dim]

    def fits(got, want):
        return len(got) == len(want) and all(g < 0 or g == w for g, w in zip(got, want))

    if not inputs or not fits(shape(inputs[0]), app["input"]):
        errs.append(f"input must be {app['input']}, got {[shape(i) for i in inputs]}")
    if not m.graph.output or not fits(shape(m.graph.output[0]), app["output"]):
        errs.append(f"output must be {app['output']}, got {[shape(o) for o in m.graph.output]}")
    meta = {p.key: p.value for p in m.metadata_props}
    for k, want in app["match"].items():
        if meta.get(k) != want:
            errs.append(f"metadata {k} must be {want!r}, got {meta.get(k)!r}")
    for k in app["slots"][e["slot"]]["require"]:
        if not meta.get(k):
            errs.append(f"metadata {k} is required for the {e['slot']} slot")
    if "default_joint_pos" in app["slots"][e["slot"]]["require"] and meta.get("default_joint_pos"):
        vals = meta["default_joint_pos"].split(",")
        if len(vals) != app["output"][-1] or not all(math.isfinite(float(v)) for v in vals):
            errs.append("default_joint_pos must hold one finite number per joint")
    return errs


def check_mirrors(e: dict) -> list[str]:
    errs = []
    for u in e.get("mirrors") or []:
        try:
            data = fetch(u, e["size"])
        except Exception as ex:  # noqa: BLE001
            errs.append(f"{e['id']}: cannot download mirror {u}: {ex}")
            continue
        if (got := hashlib.sha256(data).hexdigest()) != e["sha256"]:
            errs.append(f"{e['id']}: mirror {u} serves a different file (size {len(data)}, sha256 {got})")
    return errs


def check_files(ix: dict) -> list[str]:
    errs = []
    CACHE.mkdir(parents=True, exist_ok=True)
    for e in ix.get("policies") or []:
        errs += check_mirrors(e)
        cached = CACHE / f"{e['sha256']}.onnx"
        data = cached.read_bytes() if cached.exists() else None
        if data is None or hashlib.sha256(data).hexdigest() != e["sha256"]:
            try:
                data = fetch(e["url"], e["size"])
            except Exception as ex:  # noqa: BLE001
                errs.append(f"{e['id']}: cannot download {e['url']}: {ex}")
                continue
        got = hashlib.sha256(data).hexdigest()
        if len(data) != e["size"]:
            errs.append(f"{e['id']}: size is {len(data)}, the index says {e['size']}")
        if got != e["sha256"]:
            errs.append(f"{e['id']}: sha256 is {got}, the index says {e['sha256']}")
            continue
        cached.write_bytes(data)
        bad = check_model(e, data)
        errs += [f"{e['id']}: {x}" for x in bad]
        if not bad:
            print(f"  ok  {e['id']}", file=sys.stderr)
    return errs


def table(ix: dict, lang: str) -> str:
    zh = lang == "zh"
    head = "| 策略 | 替换 | 作者 | 许可 | 说明 |" if zh else "| Policy | Replaces | Author | License | Notes |"
    rows = [head, "| --- | --- | --- | --- | --- |"]
    for e in ix.get("policies") or []:
        app = APPS[e["app"]]
        name = (e.get("name_zh") if zh else None) or e["name"]
        desc = ((e.get("description_zh") if zh else None) or e.get("description") or "").strip()
        desc = desc.split("。")[0] + "。" if zh and "。" in desc else desc.split(". ")[0].rstrip(".") + ("." if desc else "")
        link = e.get("homepage") or e["url"]
        extra = f" [{'视频' if zh else 'video'}]({e['video']})" if e.get("video") else ""
        slot = f"{app['name'][lang]} · {app['slots'][e['slot']][lang]}"
        lic = e["license"].split(" (")[0]
        if lic == "unspecified":
            lic = "未声明" if zh else "not stated"
        rows.append(f"| [{name}]({link}) | {slot} | {e['author']} | {lic} | {desc}{extra} |")
    return "\n".join(rows)


def render(ix: dict, write: bool) -> list[str]:
    errs = []
    for lang, path in READMES.items():
        text = path.read_text(encoding="utf-8")
        new = re.sub(r"(<!-- policies:start -->\n).*?(\n<!-- policies:end -->)", lambda m: m.group(1) + table(ix, lang) + m.group(2), text, flags=re.S)
        if new == text:
            continue
        if write:
            path.write_text(new, encoding="utf-8")
            print(f"updated {path.name}", file=sys.stderr)
        else:
            errs.append(f"{path.name}: the policy table is out of date (run: uv run tools/index.py table)")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check", "table"])
    ap.add_argument("--offline", action="store_true", help="skip downloading the models")
    a = ap.parse_args()
    ix = load()
    errs = check_schema(ix)
    if errs:
        print("\n".join("✗ " + e for e in errs), file=sys.stderr)
        return 1
    if a.cmd == "table":
        render(ix, True)
        return 0
    errs = render(ix, False)
    if not a.offline:
        errs += check_files(ix)
    if errs:
        print("\n".join("✗ " + e for e in errs), file=sys.stderr)
        return 1
    print(f"✓ {len(ix.get('policies') or [])} policies OK", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
