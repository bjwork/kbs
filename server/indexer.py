#!/usr/bin/env python3
"""索引管理：扫 notes/ 重建 SQLite（元数据 + FTS5 全文索引）。

设计：markdown 文件是数据本体，SQLite 只是可丢弃的索引。
任何写入操作（新增/编辑/删除笔记）后调用 reindex() 保持同步。

全文索引：FTS5 unicode61。中文无空格分词，unicode61 会把整段中文当一个
token，所以索引前用 insert_space 在每两个汉字间插空格，把中文变成按单字
切分。查询端做同样的处理，匹配粒度 = 单字序列，正确性等价于子串匹配
（召回略宽：「回表」也会命中「回…表…」不相邻文本，靠 bm25 排序压住噪音）。
"""
import re
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from build_index import parse_frontmatter  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "server" / "data" / "kbs.db"
NOTES_DIR = ROOT / "notes"

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    name TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    date TEXT,
    category TEXT,
    tags TEXT,          -- JSON 数组字符串
    related TEXT,       -- JSON 数组字符串
    status TEXT,
    mtime REAL NOT NULL
);
"""
FTS_SCHEMA = (
    "CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts "
    "USING fts5(name UNINDEXED, title, body, tokenize='unicode61')"
)

_CJK = re.compile(r"([一-鿿])(?=[一-鿿])")
_strip_fm = re.compile(r"^---\n.*?\n---\n", re.DOTALL)


def insert_space(text: str) -> str:
    """相邻汉字之间插空格，让 unicode61 把中文切成单字。"""
    return _CJK.sub(r"\1 ", text)


def note_body(text: str) -> str:
    """去掉 frontmatter 后的正文，用于全文索引。"""
    return _strip_fm.sub("", text)


def reindex() -> dict:
    """全量 upsert + 删除孤儿行。返回统计。"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.execute(FTS_SCHEMA)

    files = {p.name: p for p in NOTES_DIR.glob("*.md")}
    db_rows = {r[0] for (r,) in conn.execute("SELECT name FROM notes")}
    # 文件内容没变但 rel_score 重写过 frontmatter（related 变化）时 mtime 也会变，
    # 为了索引与文件强一致这里直接全量 upsert（几百到几千篇都是秒级，不值得维护增量状态）
    removed = 0
    for name, path in files.items():
        mtime = path.stat().st_mtime
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if not fm.get("title"):
            continue
        conn.execute(
            "INSERT OR REPLACE INTO notes VALUES (?,?,?,?,?,?,?,?)",
            (name, fm["title"], fm.get("date", ""), fm.get("category", ""),
             str(fm.get("tags") or []), str(fm.get("related") or []),
             fm.get("status", ""), mtime),
        )
        conn.execute("DELETE FROM notes_fts WHERE name = ?", (name,))
        conn.execute(
            "INSERT INTO notes_fts VALUES (?,?,?)",
            (name, insert_space(fm["title"]), insert_space(note_body(text))),
        )
    for name in db_rows:
        if name not in files:
            conn.execute("DELETE FROM notes WHERE name = ?", (name,))
            conn.execute("DELETE FROM notes_fts WHERE name = ?", (name,))
            removed += 1
    conn.commit()
    conn.close()
    return {"total": len(files), "removed": removed}


if __name__ == "__main__":
    start = time.time()
    stats = reindex()
    print(f"索引完成：{stats}，耗时 {time.time()-start:.2f}s")
