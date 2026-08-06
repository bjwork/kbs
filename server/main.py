#!/usr/bin/env python3
"""fuxi 知识库本地服务：检索 + 录入 + 文件上传。

用法：
    pip3 install fastapi uvicorn python-multipart
    python3 server/main.py          # 起在 0.0.0.0:8000，局域网内手机可访问

设计约束：
- markdown 文件是数据本体，SQLite 只是索引（server/data/kbs.db，可删可重建）
- 删除笔记只移入 trash/，不真删（红线）
- 关联打分复用 scripts/rel_score.py 的增量打分
"""
import json
import re
import shutil
import sqlite3
import subprocess
import sys
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_index import parse_frontmatter  # noqa: E402
from indexer import DB_PATH, NOTES_DIR, insert_space, note_body, reindex  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "raw"
TRASH_DIR = ROOT / "trash"

CATEGORIES = ["ai-practice", "product-thinking", "tech", "writing", "reading", "misc"]
# 上传转换管线的格式白名单：扩展名 -> 转换方式
CONVERTERS = {".md", ".txt", ".pdf", ".docx", ".html", ".htm", ".py", ".java", ".js", ".ts", ".go", ".sql", ".sh"}

_filename_guard = re.compile(r"^[\w一-鿿.-]+$")


def _safe_name(name: str) -> str:
    """笔记文件名白名单校验：拒绝路径穿越和奇怪字符。"""
    if not name or name in (".", "..") or not _filename_guard.match(name):
        raise HTTPException(400, "非法文件名")
    return name

app = FastAPI(title="fuxi KB")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _parse_list(s: str) -> list:
    """notes.tags/related 存的是 str(list)，转回 list。"""
    try:
        return json.loads(s.replace("'", '"')) if s else []
    except (ValueError, json.JSONDecodeError):
        return []


def _note_dict(row: sqlite3.Row, with_related: bool = False) -> dict:
    out = {
        "name": row["name"],
        "title": row["title"],
        "date": row["date"],
        "category": row["category"],
        "tags": _parse_list(row["tags"]),
        "status": row["status"],
    }
    if with_related:
        out["related"] = _parse_list(row["related"])
    return out


# ---------- 检索 ----------

@app.get("/api/notes")
def list_notes(
    q: str = Query("", description="全文搜索词"),
    category: str = Query(""),
    tag: str = Query(""),
    date_from: str = Query(""),
    date_to: str = Query(""),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
):
    conn = db()
    where, params = [], []
    if category:
        where.append("n.category = ?")
        params.append(category)
    if tag:
        where.append("n.tags LIKE ?")
        params.append(f"%'{tag}'%")
    if date_from:
        where.append("n.date >= ?")
        params.append(date_from)
    if date_to:
        where.append("n.date <= ?")
        params.append(date_to)
    cond = ("WHERE " + " AND ".join(where)) if where else ""

    if q.strip():
        match = insert_space(q.strip()).replace('"', ' ')
        # 双引号包成短语查询：词序相邻才命中（中文单字索引下正确性等价于子串匹配），
        # 也避免用户输入里的引号/FTS 语法字符触发语法错误
        match = f'"{match}"'
        base = f"""
            FROM notes_fts f JOIN notes n ON n.name = f.name
            WHERE notes_fts MATCH ? {'AND ' + ' AND '.join(where) if where else ''}
        """
        total = conn.execute(f"SELECT COUNT(*) {base}", [match] + params).fetchone()[0]
        rows = conn.execute(
            f"SELECT n.*, bm25(notes_fts) AS rank {base} ORDER BY rank LIMIT ? OFFSET ?",
            [match] + params + [size, (page - 1) * size],
        ).fetchall()
    else:
        total = conn.execute(f"SELECT COUNT(*) FROM notes n {cond}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT n.* FROM notes n {cond} ORDER BY n.date DESC, n.name DESC LIMIT ? OFFSET ?",
            params + [size, (page - 1) * size],
        ).fetchall()
    conn.close()
    return {"total": total, "page": page, "size": size, "items": [_note_dict(r) for r in rows]}


@app.get("/api/notes/{name}")
def get_note(name: str):
    name = _safe_name(name)
    path = NOTES_DIR / name
    if not path.exists() or not name.endswith(".md"):
        raise HTTPException(404, "笔记不存在")
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    return {
        "name": name,
        "title": fm.get("title", ""),
        "date": fm.get("date", ""),
        "category": fm.get("category", ""),
        "tags": fm.get("tags") or [],
        "related": fm.get("related") or [],
        "status": fm.get("status", ""),
        "body": note_body(text),
    }


@app.get("/api/tags")
def list_tags():
    conn = db()
    rows = conn.execute("SELECT tags FROM notes").fetchall()
    cat_rows = conn.execute("SELECT category, COUNT(*) FROM notes GROUP BY category").fetchall()
    conn.close()
    freq = {}
    for r in rows:
        for t in _parse_list(r[0]):
            freq[t] = freq.get(t, 0) + 1
    return {
        "tags": sorted(freq.items(), key=lambda x: -x[1]),
        "categories": CATEGORIES,
        "cat_count": {r[0]: r[1] for r in cat_rows},
    }


# ---------- 录入 ----------

class NoteIn(BaseModel):
    title: str
    category: str = "misc"
    tags: list[str] = []
    body: str = ""
    name: str = ""      # 编辑时传原文件名；新建时留空由服务端生成
    raw_file: str = ""  # 关联的 raw/ 文件名（上传场景）


def _slugify(title: str) -> str:
    """标题转文件名 slug：保留中英文数字，其余转连字符，截 40 字符。"""
    s = re.sub(r"[^\w一-鿿-]+", "-", title.strip().lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)[:40].strip("-") or "untitled"


def _write_note(name: str, note: NoteIn) -> None:
    tags = ", ".join(note.tags)
    related_line = f"related_raw: {note.raw_file}\n" if note.raw_file else ""
    text = (
        f"---\ntitle: {note.title}\ndate: {date.today().isoformat()}\n"
        f"category: {note.category}\ntags: [{tags}]\nstatus: raw\n{related_line}---\n\n"
        f"{note.body.strip()}\n"
    )
    (NOTES_DIR / name).write_text(text, encoding="utf-8")


@app.post("/api/notes")
def save_note(note: NoteIn):
    if not note.title.strip():
        raise HTTPException(400, "标题不能为空")
    if note.category not in CATEGORIES:
        raise HTTPException(400, f"category 必须是：{CATEGORIES}")
    if note.name:  # 编辑
        name = _safe_name(note.name)
        old = NOTES_DIR / name
        if not old.exists():
            raise HTTPException(404, "被编辑的笔记不存在")
    else:  # 新建
        name = f"{date.today().isoformat()}-{_slugify(note.title)}.md"
        if (NOTES_DIR / name).exists():
            raise HTTPException(409, f"同名笔记已存在：{name}")
    _write_note(name, note)
    # 关联重算（增量，复用 rel_score.py）
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "rel_score.py"), name],
        cwd=ROOT, capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise HTTPException(500, f"关联重算失败：{r.stderr[:200]}")
    stats = reindex()
    return {"name": name, "index": stats}


@app.delete("/api/notes/{name}")
def delete_note(name: str):
    """删除 = 移入 trash/，不真删（红线）。"""
    name = _safe_name(name)
    src = NOTES_DIR / name
    if not src.exists() or not name.endswith(".md"):
        raise HTTPException(404, "笔记不存在")
    TRASH_DIR.mkdir(exist_ok=True)
    dst = TRASH_DIR / name
    if dst.exists():
        dst = TRASH_DIR / f"{date.today().isoformat()}-{name}"
    shutil.move(str(src), str(dst))
    stats = reindex()
    return {"moved_to": str(dst.relative_to(ROOT)), "index": stats}


# ---------- 文件上传 ----------

def _convert(src: Path, suffix: str) -> str:
    """原始文件 → 纯文本。失败抛 HTTPException。"""
    if suffix == ".pdf":
        r = subprocess.run(
            ["pdftotext", str(src), "-"], capture_output=True, text=True,
        )
        if r.returncode != 0:
            raise HTTPException(500, f"pdftotext 失败：{r.stderr[:200]}")
        clean = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "clean_pdf_text.py")],
            input=r.stdout, capture_output=True, text=True,
        )
        return clean.stdout
    if suffix == ".docx":
        r = subprocess.run(
            ["textutil", "-convert", "txt", "-stdout", str(src)],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            raise HTTPException(500, "textutil 转换 docx 失败")
        return r.stdout
    if suffix in (".html", ".htm"):
        text = src.read_text(encoding="utf-8", errors="ignore")
        text = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", "", text, flags=re.I)
        text = re.sub(r"<[^>]+>", "\n", text)
        return re.sub(r"\n{3,}", "\n\n", text).strip()
    # md / txt / 代码文件直接读
    return src.read_text(encoding="utf-8", errors="ignore")


@app.post("/api/upload")
async def upload(file: UploadFile):
    safe_base = _safe_name(Path(file.filename).name)
    suffix = Path(safe_base).suffix.lower()
    if suffix not in CONVERTERS:
        raise HTTPException(400, f"不支持的格式 {suffix}，支持：{sorted(CONVERTERS)}")
    RAW_DIR.mkdir(exist_ok=True)
    raw_name = f"{date.today().isoformat()}-{safe_base}"
    raw_path = RAW_DIR / raw_name
    if raw_path.exists():
        raise HTTPException(409, f"raw/ 已存在同名文件：{raw_name}")
    raw_path.write_bytes(await file.read())
    # 二进制原件同时留纯文本 .md 版（CLAUDE.md 规则）；文本类源文件不必再存一份
    if suffix in (".pdf", ".docx", ".html", ".htm"):
        text = _convert(raw_path, suffix)
        (RAW_DIR / (raw_path.stem + ".md")).write_text(text, encoding="utf-8")
    else:
        text = raw_path.read_text(encoding="utf-8", errors="ignore")
    return {"raw_file": raw_name, "text": text}


# ---------- 静态文件（PWA 前端） ----------

app.mount("/", StaticFiles(directory=ROOT / "web", html=True), name="web")


if __name__ == "__main__":
    reindex()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
