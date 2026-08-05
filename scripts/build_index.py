#!/usr/bin/env python3
"""扫描 notes/ 下所有笔记的 frontmatter，按分类 + 标签生成 INDEX.md。

用法：
    python3 scripts/build_index.py          # 从 notes/ 生成 INDEX.md
    python3 scripts/build_index.py --root /path/to/kb
"""
import argparse
import re
import sys
from datetime import date
from pathlib import Path

FM_PATTERN = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
LIST_LINE = re.compile(r"^\s+-\s+(.*)$")


def _parse_inline(value: str):
    """解析行内值：'[a, b]' → 列表；其他 → 字符串。"""
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [v.strip() for v in inner.split(",")] if inner else []
    return value


def parse_frontmatter(text: str) -> dict:
    """解析最小 YAML 子集：key: value、key: [a, b] 行内列表、key: 后跟 '- item' 列表。"""
    m = FM_PATTERN.match(text)
    if not m:
        return {}
    fm = {}
    current_key = None
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        list_item = LIST_LINE.match(line)
        if list_item and current_key:
            if not isinstance(fm.get(current_key), list):
                fm[current_key] = []
            fm[current_key].append(list_item.group(1).strip())
            continue
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            current_key = key
            fm[key] = _parse_inline(value) if value else []
    return fm


def load_notes(notes_dir: Path) -> list:
    notes = []
    for path in sorted(notes_dir.glob("*.md")):
        fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        if not fm.get("title"):
            continue
        notes.append({"file": path.name, "fm": fm})
    return notes


def render(notes: list) -> str:
    by_category = {}
    tag_count = {}
    for n in notes:
        cat = n["fm"].get("category") or "未分类"
        by_category.setdefault(cat, []).append(n)
        tags = n["fm"].get("tags") or []
        for t in tags:
            tag_count[t] = tag_count.get(t, 0) + 1

    lines = [
        "# INDEX",
        "",
        f"> 自动生成，请勿手改。共 {len(notes)} 篇，更新于 {date.today().isoformat()}",
        "",
        "## 按分类",
        "",
    ]
    for cat in sorted(by_category):
        lines.append(f"### {cat}")
        for n in by_category[cat]:
            title = n["fm"]["title"]
            tags = " ".join(f"`{t}`" for t in (n["fm"].get("tags") or []))
            lines.append(f"- [[{n['file']}]] {title} {tags}".rstrip())
        lines.append("")

    lines += ["## 按标签", ""]
    for tag, cnt in sorted(tag_count.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- `{tag}` × {cnt}")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    args = ap.parse_args()
    root = Path(args.root)
    notes = load_notes(root / "notes")
    if not notes:
        print("notes/ 下没有带 title 的笔记", file=sys.stderr)
        sys.exit(1)
    out = root / "INDEX.md"
    out.write_text(render(notes), encoding="utf-8")
    print(f"INDEX.md 已生成：{len(notes)} 篇")


if __name__ == "__main__":
    main()
