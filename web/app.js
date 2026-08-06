/* fuxi 知识库前端：列表检索 / 详情 / 记笔记 / 上传。无框架，原生 fetch。 */
const app = document.getElementById('app');
const state = { page: 1, size: 50, tagFreq: [], editing: '' };

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function toast(msg) {
  const el = document.createElement('div');
  el.className = 'toast'; el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2500);
}

let timer;
function debouncedSearch() { clearTimeout(timer); timer = setTimeout(() => loadList(1), 300); }

async function api(path, opts) {
  const r = await fetch(path, opts);
  if (!r.ok) {
    let msg = r.statusText;
    try { msg = (await r.json()).detail || msg; } catch {}
    throw new Error(msg);
  }
  return r.json();
}

/* ---------- 列表 ---------- */
async function loadList(page) {
  state.page = page;
  const q = document.getElementById('q').value.trim();
  const cat = document.getElementById('f-category').value;
  const tag = document.getElementById('f-tag').value;
  const p = new URLSearchParams({ page, size: state.size });
  if (q) p.set('q', q);
  if (cat) p.set('category', cat);
  if (tag) p.set('tag', tag);
  const data = await api('/api/notes?' + p);
  if (!data.items.length) { app.innerHTML = '<div class="empty">没有匹配的笔记</div>'; return; }
  const pages = Math.ceil(data.total / data.size);
  app.innerHTML = `
    <div class="total-line">共 ${data.total} 篇${pages > 1 ? `，第 ${page}/${pages} 页` : ''}</div>
    ${data.items.map(n => `
      <div class="note-item" onclick="showDetail('${esc(n.name)}')">
        <h3>${esc(n.title)}</h3>
        <div class="meta">${esc(n.date)} · ${esc(n.category)}
          ${n.tags.map(t => `<span class="tag">${esc(t)}</span>`).join('')}</div>
      </div>`).join('')}
    ${pages > 1 ? `<div class="pager">
      ${page > 1 ? '<button onclick="loadList(' + (page-1) + ')">上一页</button>' : ''}
      ${page < pages ? '<button onclick="loadList(' + (page+1) + ')">下一页</button>' : ''}
    </div>` : ''}`;
}

/* ---------- 详情 ---------- */
async function showDetail(name) {
  const n = await api('/api/notes/' + encodeURIComponent(name));
  app.innerHTML = `
    <div class="back-bar">
      <button onclick="loadList(state.page)">← 返回</button>
      <button onclick='showForm(${JSON.stringify(n).replace(/'/g, "&#39;")})'>编辑</button>
      <button class="danger" onclick="delNote('${esc(name)}')">删除</button>
    </div>
    <h2>${esc(n.title)}</h2>
    <div class="meta" style="margin:6px 0 14px">${esc(n.date)} · ${esc(n.category)}
      ${n.tags.map(t => `<span class="tag">${esc(t)}</span>`).join('')}</div>
    <div class="detail-body">${esc(n.body)}</div>
    ${n.related.length ? `<div class="related-list"><b>相关笔记</b>
      ${n.related.map(r => `<a onclick="showDetail('${esc(r)}')">${esc(r)}</a>`).join('')}</div>` : ''}`;
  window.scrollTo(0, 0);
}

async function delNote(name) {
  if (!confirm('删除后移入 trash/（不真删），确定？')) return;
  await api('/api/notes/' + encodeURIComponent(name), { method: 'DELETE' });
  toast('已移入 trash/');
  loadList(1);
}

/* ---------- 记笔记 / 编辑 ---------- */
function showForm(note) {
  note = note || {};
  state.editing = note.name || '';
  const sel = new Set(note.tags || []);
  app.innerHTML = `
    <div class="back-bar"><button onclick="loadList(state.page)">← 取消</button></div>
    <h2>${note.name ? '编辑笔记' : '记笔记'}</h2>
    <div style="height:12px"></div>
    <div class="form-row"><label>标题</label><input type="text" id="f-title" value="${esc(note.title || '')}"></div>
    <div class="form-row"><label>分类</label><select id="f-cat">
      ${CATEGORIES.map(c => `<option ${c === note.category ? 'selected' : ''}>${c}</option>`).join('')}</select></div>
    <div class="form-row"><label>标签（点选，来自标签体系）</label>
      <div class="tag-pick" id="f-tags">
        ${state.tagFreq.map(([t]) => `<span class="tag ${sel.has(t) ? 'on' : ''}" onclick="this.classList.toggle('on')">${esc(t)}</span>`).join('')}
      </div></div>
    <div class="form-row"><label>正文（markdown）</label><textarea id="f-body">${esc(note.body || '')}</textarea></div>
    <button class="primary" onclick="saveNote()">保存</button>`;
  window.scrollTo(0, 0);
}

async function saveNote() {
  const tags = [...document.querySelectorAll('#f-tags .tag.on')].map(e => e.textContent);
  const payload = {
    title: document.getElementById('f-title').value,
    category: document.getElementById('f-cat').value,
    tags, body: document.getElementById('f-body').value,
    name: state.editing, raw_file: state.rawFile || '',
  };
  try {
    const r = await api('/api/notes', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    state.rawFile = '';
    toast('已保存：' + r.name);
    showDetail(r.name);
  } catch (e) { toast('保存失败：' + e.message); }
}

/* ---------- 上传 ---------- */
function showUpload() {
  app.innerHTML = `
    <div class="back-bar"><button onclick="loadList(state.page)">← 取消</button></div>
    <h2>上传文件入库</h2>
    <div style="height:12px"></div>
    <div class="form-row"><label>支持 pdf / docx / html / md / txt / 代码文件</label>
      <input type="file" id="f-file"></div>
    <button class="primary" onclick="doUpload()">转换并去写笔记</button>
    <div id="up-result"></div>`;
}

async function doUpload() {
  const f = document.getElementById('f-file').files[0];
  if (!f) { toast('先选文件'); return; }
  const fd = new FormData(); fd.append('file', f);
  toast('转换中…');
  try {
    const r = await api('/api/upload', { method: 'POST', body: fd });
    state.rawFile = r.raw_file;
    // 纯文本预填到笔记表单正文，用户补摘要和立场
    showForm({ title: f.filename.replace(/\.[^.]+$/, ''), body: r.text });
    toast('已存 raw/' + r.raw_file + '，请补摘要和立场');
  } catch (e) { toast('上传失败：' + e.message); }
}

/* ---------- 启动 ---------- */
let CATEGORIES = [];
(async function init() {
  const t = await api('/api/tags');
  state.tagFreq = t.tags;
  CATEGORIES = t.categories;
  document.getElementById('f-category').innerHTML =
    '<option value="">全部分类</option>' + CATEGORIES.map(c => `<option>${c}</option>`).join('');
  document.getElementById('f-tag').innerHTML =
    '<option value="">全部标签</option>' + t.tags.map(([x, n]) => `<option value="${esc(x)}">${esc(x)} (${n})</option>`).join('');
  loadList(1);
})();
