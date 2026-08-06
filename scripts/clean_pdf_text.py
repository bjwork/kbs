#!/usr/bin/env python3
"""从 pdftotext 输出中提取专栏正文：剔除页眉/页脚/URL 装饰行。

用法：
    pdftotext xxx.pdf - | python3 scripts/clean_pdf_text.py
    python3 scripts/clean_pdf_text.py input.txt output.md
"""
import re
import sys

# 装饰行特征：
# - "2026/8/5 16:36" 这类时间戳页眉
# - file:/// 开头的本地文件 URL
# - "1/8" 页码
# - "01 | 基础架构：..." 重复出现的章节标题页眉（与正文首行重复）
DATE_HEADER = re.compile(r"^\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}\s*$")
FILE_URL = re.compile(r"^file:///\S*")
PAGE_NUM = re.compile(r"^\d+/\d+\s*$")
LESSON_HEADER = re.compile(r"^\d{2}\s*\|\s*")  # "01 | xxx" 页眉
SPEAKER_LINE = re.compile(r"^林晓斌（丁奇）·\s*MySQL实战45讲\s*$")

# 页尾「笔记/复制/AI 翻译」等 UI 残骸：正文结束后的一串碎片行。
# 特征：最后 N 行里出现「复制」「翻译」「总结」等孤立词，且行长普遍 ≤6 字。
UI_TOKENS = {"笔记", "复制", "AI", "深入了解", "翻译", "解释", "总结",
             "英语", "中文简体", "法语", "德语", "日语", "韩语", "俄语", "西班牙语"}


def _strip_ui_tail(lines: list) -> list:
    """从尾部往回找第一个『正文行』（长度 > 10 或含句号/问号/冒号），其后的 UI 残骸全部砍掉。"""
    end = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if not line:
            continue
        if line in UI_TOKENS:
            end = i
            continue
        # 真正的正文行：长句或带标点
        if len(line) > 10 or re.search(r"[。？！：；]", line):
            break
        # 短行但不是 UI 词（比如代码片段），保守保留——再往前看一行
        end = i
    return lines[:end + 1]


def clean(text: str) -> str:
    out = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            out.append("")
            continue
        if DATE_HEADER.match(line):
            continue
        if FILE_URL.match(line):
            continue
        if PAGE_NUM.match(line):
            continue
        if LESSON_HEADER.match(line):
            continue
        if SPEAKER_LINE.match(line):
            continue
        out.append(raw.rstrip())
    # 折叠连续空行
    collapsed = []
    prev_blank = False
    for line in out:
        if line == "":
            if prev_blank:
                continue
            prev_blank = True
        else:
            prev_blank = False
        collapsed.append(line)
    return "\n".join(_strip_ui_tail(collapsed)).strip() + "\n"


if __name__ == "__main__":
    if len(sys.argv) == 3:
        text = open(sys.argv[1], encoding="utf-8").read()
        open(sys.argv[2], "w", encoding="utf-8").write(clean(text))
    else:
        sys.stdout.write(clean(sys.stdin.read()))
