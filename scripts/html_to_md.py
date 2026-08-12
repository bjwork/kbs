#!/usr/bin/env python3
"""极客时间 slate editor HTML → 纯正文 Markdown。

针对极客时间专栏页面渲染后的 HTML：正文包在 data-slate-string="true" 的 span 里，
按 data-slate-object="block" 分段（paragraph / heading / list-line）。
剥掉标签、CSS、JS、导航，只留正文。

用法：
    python3 scripts/html_to_md.py input.html output.md
    python3 scripts/html_to_md.py k8s_lesson_html/ raw_prefix:2026-08-12-   # 批量
"""
import argparse
import html
import re
import sys
from pathlib import Path

# block 开标签：<任意标签 ... data-slate-object="block" ...>（heading 是 <h2>，list-line/list 是 <div>）
BLOCK_OPEN = re.compile(r'<(\w+)\s+[^>]*data-slate-object="block"([^>]*)>')
# block 内文本：<span data-slate-string="true">文本</span>
SLATE_STRING = re.compile(r'data-slate-string="true">(.*?)</span>', re.DOTALL)
# 类型标记
TYPE_VAL = re.compile(r'data-slate-type="([^"]+)"')
# <title>...</title>
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL)
# 作者行：<div class="author">张磊 · 深入剖析 Kubernetes</div>
AUTHOR_RE = re.compile(r'<div class="author">(.*?)</div>', re.DOTALL)


def _strip_tags(s: str) -> str:
    """去掉残留的子标签（如 annotation span 嵌套），只留文本。"""
    return re.sub(r"<[^>]+>", "", s)


def _extract_blocks(html_text: str) -> list:
    """切 block，返回 (kind, text) 列表。kind ∈ {h, li, code, p}。"""
    blocks = []
    for m in BLOCK_OPEN.finditer(html_text):
        tag = m.group(1)
        attrs = m.group(2)
        # 从开标签起到下一个同级 block 开标签为止，截取该 block 片段
        start = m.end()
        nxt = BLOCK_OPEN.search(html_text, start)
        end = nxt.start() if nxt else len(html_text)
        frag = html_text[start:end]

        texts = SLATE_STRING.findall(frag)
        if not texts:
            continue
        line = "".join(_strip_tags(html.unescape(t)) for t in texts)
        if not line.strip():
            continue

        type_m = TYPE_VAL.search(m.group(0))
        stype = type_m.group(1) if type_m else ""
        if tag == "h2" or stype == "heading":
            blocks.append(("h", line))
        elif stype == "list-line":
            blocks.append(("li", line))
        elif stype == "code-line":
            blocks.append(("code", line))
        else:
            blocks.append(("p", line))
    return blocks


def convert(html_text: str) -> str:
    """HTML 全文 → 纯正文 md。"""
    title_m = TITLE_RE.search(html_text)
    title = html.unescape(title_m.group(1).strip()) if title_m else ""
    # 标题里的 " | " 极客时间用全角竖线分隔模块名，保留原样

    author_m = AUTHOR_RE.search(html_text)
    author = html.unescape(author_m.group(1).strip()) if author_m else ""

    blocks = _extract_blocks(html_text)

    out = []
    if title:
        out.append(f"# {title}")
        out.append("")
    if author:
        out.append(f"> {author}")
        out.append("")
    prev_kind = None
    for kind, text in blocks:
        if kind == "h":
            out.append("")
            out.append(f"## {text}")
        elif kind == "li":
            # 连续 li 之间不插空行，模拟列表
            if prev_kind != "li":
                out.append("")
            out.append(f"- {text}")
        elif kind == "code":
            if prev_kind != "code":
                out.append("")
            out.append(f"    {text}")
        else:
            if prev_kind == "li":
                out.append("")
            out.append(text)
        prev_kind = kind
    out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="单个 HTML 文件，或批量目录")
    ap.add_argument("output", nargs="?", help="单个输出 md；批量时省略")
    ap.add_argument("--prefix", default="", help="批量模式输出文件名前缀，如 2026-08-12-")
    args = ap.parse_args()

    src = Path(args.input)
    if src.is_dir():
        # 批量：input 是目录，--prefix 给输出名加前缀，写到该目录下
        out_dir = Path(args.output) if args.output else src
        out_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for h in sorted(src.glob("*.html")):
            md = convert(h.read_text(encoding="utf-8"))
            out_path = out_dir / f"{args.prefix}{h.stem}.md"
            out_path.write_text(md, encoding="utf-8")
            count += 1
            print(f"  {h.name} → {out_path.name}")
        print(f"批量转换完成：{count} 个文件")
    else:
        if not args.output:
            print("单文件模式需要指定输出路径", file=sys.stderr)
            sys.exit(1)
        md = convert(src.read_text(encoding="utf-8"))
        Path(args.output).write_text(md, encoding="utf-8")
        print(f"{src.name} → {args.output}")


if __name__ == "__main__":
    main()
