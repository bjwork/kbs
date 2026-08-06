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


# 反规范化标签：出现频率过高、失去区分度的标签不计分。
# 绝对阈值，随库规模手动调整：48 篇时 20（挡掉了 reading×45 这类大标签）；
# 库涨到几千篇时需要重校（比如 2000 篇调到 ~200）。
TAG_DF_THRESHOLD = 20


def _title_fragments(title: str, min_len: int = 3) -> set:
    """标题分片，用于倒排预筛：英文/数字词 + 中文段的全部 ≥min_len 滑窗子串。"""
    frags = set()
    for word in re.findall(r"[a-z0-9]+", title.lower()):
        if word not in STOPWORDS and len(word) > 2:
            frags.add(word)
    for seg in re.findall(r"[一-鿿]+", title):
        for i in range(len(seg) - min_len + 1):
            frags.add(seg[i:i + min_len])
    return frags


def build_inverted(notes: list) -> dict:
    """倒排索引：fragment(标签加 'tag:' 前缀) -> 笔记文件名集合。供增量预筛。"""
    inv = {}
    for n in notes:
        keys = {f"tag:{t}" for t in (n["fm"].get("tags") or [])}
        keys |= _title_fragments(n["fm"]["title"])
        for k in keys:
            inv.setdefault(k, set()).add(n["file"])
    return inv


def candidates(target: dict, inv: dict) -> set:
    """预筛候选：与 target 共享任一标签或任一标题分片的笔记。
    共享标签或标题子串才可能过 4 分阈值，其余直接跳过（零分对不再逐一打分）。"""
    keys = {f"tag:{t}" for t in (target["fm"].get("tags") or [])}
    keys |= _title_fragments(target["fm"]["title"])
    out = set()
    for k in keys:
        out |= inv.get(k, set())
    out.discard(target["file"])
    return out
# 系列笔记识别：匹配「日期-系列名编号-标题」里的「系列名编号」段。
# 兼容「mysql45-01」「series01」「java-36」等写法，取到第一个全数字段为止。
SERIES_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z]+)*-\d+)")


def _series_prefix(filename: str):
    m = SERIES_PREFIX_RE.match(filename)
    return m.group(1) if m else None


def score(new: dict, old: dict, tag_df: dict = None) -> int:
    new_tags = set(new["fm"].get("tags") or [])
    old_tags = set(old["fm"].get("tags") or [])
    if tag_df:
        new_tags = {t for t in new_tags if tag_df.get(t, 0) < TAG_DF_THRESHOLD}
        old_tags = {t for t in old_tags if tag_df.get(t, 0) < TAG_DF_THRESHOLD}
    # 同系列笔记的标签重叠不计分（避免全套教程互相全关联）
    if _series_prefix(new["file"]) == _series_prefix(old["file"]) and _series_prefix(new["file"]):
        tag_hits = 0
    else:
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

    # 全库标签词频，用于反规范化
    tag_df = {}
    for n in notes:
        for t in set(n["fm"].get("tags") or []):
            tag_df[t] = tag_df.get(t, 0) + 1

    # edges: file -> set(related files)
    edges = {n["file"]: set(n["fm"].get("related") or []) for n in notes}
    inv = build_inverted(notes)
    by_file = {n["file"]: n for n in notes}
    for t in targets:
        # 先摘掉自己：旧 edges 里指向 t 的引用全部清掉，再以新结果为准回写
        for rel_set in edges.values():
            rel_set.discard(t["file"])
        pool = notes if args.all else [by_file[f] for f in candidates(t, inv) if f in by_file]
        new_related = set()
        for o in pool:
            if o["file"] == t["file"]:
                continue
            s = score(t, o, tag_df)
            if s >= THRESHOLD:
                new_related.add(o["file"])
                edges[o["file"]].add(t["file"])
                print(f"关联 {s} 分：{t['file']}  <->  {o['file']}")
        edges[t["file"]] = new_related
    for fname, related in edges.items():
        write_related(by_file[fname]["path"], sorted(related), args.dry_run)
    print("完成" + ("（dry-run，未写文件）" if args.dry_run else ""))


if __name__ == "__main__":
    main()
