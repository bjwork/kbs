#!/usr/bin/env python3
"""关联打分：标签重叠 ×2 + 标题关键词重叠 ×1，≥4 分判为关联，双向写入 related。

用法：
    python3 scripts/rel_score.py notes/xxx.md   # 只算指定笔记对其他笔记的关联
    python3 scripts/rel_score.py --all          # 全量重算
    python3 scripts/rel_score.py --all --dry-run # 只打印不写文件
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_index import parse_frontmatter  # noqa: E402

FM_PATTERN = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
RELATED_BLOCK = re.compile(r"^related:\n(?:\s+-\s+.*\n?)*", re.MULTILINE)

TAG_WEIGHT = 2
KW_WEIGHT = 1
THRESHOLD = 4

STOPWORDS = {
    "一个", "我们", "可以", "什么", "没有", "不是", "就是", "这个", "那个",
    "the", "and", "for", "with", "from", "that", "this", "you", "your",
}


def _common_substrings(a: str, b: str, min_len: int = 3) -> set:
    """两字符串的最长公共子串（长度 ≥ min_len），用于中文标题关键词匹配。

    2-gram 滑窗会把「知识库的」「的标」这种碎片误算成重叠；
    要求公共片段 ≥3 字能过滤掉绝大多数虚词碰撞。
    """
    hits = set()
    for i in range(len(a) - min_len + 1):
        for j in range(i + min_len, len(a) + 1):
            frag = a[i:j]
            if frag in b:
                # 只保留极大片段（不被更长命中包含）
                hits.add(frag)
            else:
                break
    # 去掉被更长命中包含的短片段
    maximal = set()
    for h in hits:
        if not any(h != o and h in o for o in hits):
            maximal.add(h)
    return maximal


def tokenize(title: str) -> set:
    """标题关键词：英文/数字按单词，中文部分保留原文用于公共子串比对。"""
    title = title.lower()
    tokens = set()
    for word in re.findall(r"[a-z0-9]+", title):
        if word not in STOPWORDS and len(word) > 2:
            tokens.add(word)
    for seg in re.findall(r"[一-鿿]+", title):
        tokens.add(seg)  # 中文整段保留，交给 common_substrings 处理
    return tokens


def _kw_overlap(title_a: str, title_b: str) -> int:
    """标题关键词重叠数：英文词集合交集 + 中文公共子串（≥3 字）数。"""
    ta, tb = tokenize(title_a), tokenize(title_b)
    en_a = {t for t in ta if not re.search(r"[一-鿿]", t)}
    en_b = {t for t in tb if not re.search(r"[一-鿿]", t)}
    hits = len(en_a & en_b)
    zh_a = " ".join(t for t in ta if re.search(r"[一-鿿]", t))
    zh_b = " ".join(t for t in tb if re.search(r"[一-鿿]", t))
    hits += len(_common_substrings(zh_a, zh_b))
    return hits


def score(new: dict, old: dict) -> int:
    new_tags = set(new["fm"].get("tags") or [])
    old_tags = set(old["fm"].get("tags") or [])
    tag_hits = len(new_tags & old_tags)
    kw_hits = _kw_overlap(new["fm"]["title"], old["fm"]["title"])
    return tag_hits * TAG_WEIGHT + kw_hits * KW_WEIGHT


def load_all(notes_dir: Path) -> list:
    notes = []
    for path in sorted(notes_dir.glob("*.md")):
        fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        if fm.get("title"):
            notes.append({"file": path.name, "path": path, "fm": fm})
    return notes


def write_related(path: Path, related: list, dry_run: bool) -> None:
    text = path.read_text(encoding="utf-8")
    m = FM_PATTERN.match(text)
    if not m:
        return
    fm_body = m.group(1)
    if RELATED_BLOCK.search(fm_body):
        fm_body = RELATED_BLOCK.sub("", fm_body).rstrip("\n")
    if related:
        block = "related:\n" + "".join(f"  - {r}\n" for r in related)
        fm_body = fm_body.rstrip("\n") + "\n" + block.rstrip("\n")
    new_text = f"---\n{fm_body}\n---\n" + text[m.end():]
    if not dry_run:
        path.write_text(new_text, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", help="notes/ 下的目标笔记")
    ap.add_argument("--all", action="store_true", help="全量重算")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    args = ap.parse_args()

    root = Path(args.root)
    notes_dir = root / "notes"
    notes = load_all(notes_dir)
    if len(notes) < 2:
        print("notes/ 下少于 2 篇，无需计算关联", file=sys.stderr)
        sys.exit(0)

    targets = notes if args.all else [n for n in notes if n["file"] == args.target]
    if not targets:
        print(f"未找到目标笔记：{args.target}", file=sys.stderr)
        sys.exit(1)

    # edges: file -> set(related files)
    edges = {n["file"]: set(n["fm"].get("related") or []) for n in notes}
    for t in targets:
        edges[t["file"]] = set()
        for o in notes:
            if o["file"] == t["file"]:
                continue
            s = score(t, o)
            if s >= THRESHOLD:
                edges[t["file"]].add(o["file"])
                edges[o["file"]].add(t["file"])
                print(f"关联 {s} 分：{t['file']}  <->  {o['file']}")

    by_file = {n["file"]: n for n in notes}
    for fname, related in edges.items():
        write_related(by_file[fname]["path"], sorted(related), args.dry_run)
    print("完成" + ("（dry-run，未写文件）" if args.dry_run else ""))


if __name__ == "__main__":
    main()
