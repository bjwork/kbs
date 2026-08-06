/* fuxi 知识库前端：三栏工作台（Vue 3 global build，无构建工具） */
const { createApp, ref, reactive, computed, onMounted, watch } = Vue;

/* ---------- 工具 ---------- */
function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function md(src) {
  return DOMPurify.sanitize(marked.parse(src || '', { breaks: true }));
}
async function api(path, opts) {
  const r = await fetch(path, opts);
  if (!r.ok) {
    let msg = r.statusText;
    try { msg = (await r.json()).detail || msg; } catch {}
    throw new Error(msg);
  }
  return r.json();
}
let _timer;
function debounce(fn, ms = 300) {
  return (...args) => { clearTimeout(_timer); _timer = setTimeout(() => fn(...args), ms); };
}

/* ---------- 全局状态 ---------- */
const store = reactive({
  categories: [], tagFreq: [],
  filters: { q: '', category: '', tag: '' },
  list: { items: [], total: 0, page: 1, size: 50 },
  current: null,        // 当前详情
  view: 'reader',       // reader | editor
  editing: { name: '', title: '', category: 'misc', tags: [], body: '', raw_file: '', url: '' },
  catCount: {},         // 分类 -> 篇数
  navOpen: false,       // 移动端抽屉
  toasts: [],
});

function toast(msg) {
  const id = Date.now() + Math.random();
  store.toasts.push({ id, msg });
  setTimeout(() => { store.toasts = store.toasts.filter(t => t.id !== id); }, 2600);
}

/* ---------- API 动作 ---------- */
async function loadList(page) {
  store.list.page = page ?? store.list.page;
  const p = new URLSearchParams({ page: store.list.page, size: store.list.size });
  const { q, category, tag } = store.filters;
  if (q) p.set('q', q);
  if (category) p.set('category', category);
  if (tag) p.set('tag', tag);
  const d = await api('/api/notes?' + p);
  store.list.items = d.items;
  store.list.total = d.total;
}

async function openNote(name) {
  store.current = await api('/api/notes/' + encodeURIComponent(name));
  store.view = 'reader';
  store.navOpen = false;
}

async function saveNote() {
  const e = store.editing;
  if (!e.title.trim()) { toast('标题不能为空'); return; }
  try {
    const r = await api('/api/notes', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(e),
    });
    toast('已保存：' + r.name);
    await loadList(store.list.page);
    await openNote(r.name);
    await refreshTags();
  } catch (err) { toast('保存失败：' + err.message); }
}

async function delNote(name) {
  if (!confirm('删除后移入 trash/（不真删），确定？')) return;
  await api('/api/notes/' + encodeURIComponent(name), { method: 'DELETE' });
  toast('已移入 trash/');
  store.current = null;
  await loadList(1);
  await refreshTags();
}

async function refreshTags() {
  const d = await api('/api/tags');
  store.tagFreq = d.tags;
  store.categories = d.categories;
  store.catCount = d.cat_count || {};
}

function startEdit(note) {
  const n = note || {};
  store.editing = {
    name: n.name || '', title: n.title || '', category: n.category || 'misc',
    tags: [...(n.tags || [])], body: n.body || '', raw_file: n.raw_file || '',
    url: n.url || '',
  };
  store.view = 'editor';
}

async function uploadFile(file) {
  if (!file) return;
  const fd = new FormData(); fd.append('file', file);
  toast('转换中…');
  try {
    const r = await api('/api/upload', { method: 'POST', body: fd });
    startEdit({ title: file.name.replace(/\.[^.]+$/, ''), body: r.text, raw_file: r.raw_file });
    toast('已存 raw/' + r.raw_file + '，请补摘要和立场');
  } catch (err) { toast('上传失败：' + err.message); }
}

const searchDebounced = debounce(() => loadList(1));

/* ---------- 组件 ---------- */
const NavPane = {
  template: `
  <aside class="nav pane" :class="{open: store.navOpen}">
    <div class="brand"><span class="logo">fuxi</span><span class="sub">知识库</span></div>
    <div class="nav-actions">
      <button class="btn primary block" @click="startEdit()">＋ 记笔记</button>
      <button class="btn block" @click="startEdit({url: '', _urlPrompt: true}); promptUrl()">🔗 丢链接</button>
      <button class="btn block" @click="$refs.file.click()">上传</button>
      <input type="file" ref="file" hidden @change="uploadFile($event.target.files[0]); $event.target.value=''">
    </div>
    <div class="nav-sec">
      <h4>分类</h4>
      <div class="nav-item" :class="{on: !store.filters.category}" @click="pick('')">全部<span class="n">{{ totalNotes }}</span></div>
      <div v-for="c in catList" :key="c.name" class="nav-item" :class="{on: store.filters.category === c.name}" @click="pick(c.name)">
        {{ c.name }}<span class="n">{{ c.n }}</span>
      </div>
    </div>
    <div class="nav-sec">
      <h4>标签</h4>
      <div class="tag-cloud">
        <span v-for="[t, n] in store.tagFreq" :key="t" class="chip" :class="{on: store.filters.tag === t}" @click="pickTag(t)">
          {{ t }}<span class="n">{{ n }}</span>
        </span>
      </div>
    </div>
  </aside>
  <div v-if="store.navOpen" class="nav-mask" @click="store.navOpen = false"></div>`,
  computed: {
    totalNotes() { return store.list.total; },
    catList() {
      return store.categories.map(name => ({ name, n: store.catCount[name] || 0 }));
    },
  },
  methods: {
    pick(c) { store.filters.category = store.filters.category === c ? '' : c; store.navOpen = false; loadList(1); },
    pickTag(t) { store.filters.tag = store.filters.tag === t ? '' : t; store.navOpen = false; loadList(1); },
    startEdit, uploadFile,
    promptUrl() {
      const url = prompt('粘贴原文链接（正文先贴到笔记里，抓取管线二期再做）：');
      if (url) store.editing.url = url.trim();
    },
  },
  data: () => ({ store }),
};

const ListPane = {
  template: `
  <section class="list pane">
    <button class="nav-toggle" @click="store.navOpen = true">☰</button>
    <div class="list-head">
      <div class="search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
        <input type="search" placeholder="全文搜索…" v-model="store.filters.q" @input="onSearch">
      </div>
      <div class="list-meta">
        <span>共 {{ store.list.total }} 篇{{ pages > 1 ? '，第 ' + store.list.page + '/' + pages + ' 页' : '' }}</span>
        <span v-if="store.filters.tag || store.filters.category">
          <button class="btn ghost" style="font-size:12px;color:var(--accent)" @click="clearFilters">清除筛选 ✕</button>
        </span>
      </div>
    </div>
    <div class="list-body">
      <div v-if="!store.list.items.length" class="empty">没有匹配的笔记</div>
      <div v-for="n in store.list.items" :key="n.name" class="note-card"
           :class="{on: store.current && store.current.name === n.name}" @click="openNote(n.name)">
        <h3>{{ n.title }}</h3>
        <div class="meta"><span>{{ n.date }}</span><span class="cat">{{ n.category }}</span></div>
        <div class="tags" v-if="n.tags.length"><span v-for="t in n.tags" :key="t" class="chip">{{ t }}</span></div>
      </div>
      <div class="pager" v-if="pages > 1">
        <button class="btn" v-if="store.list.page > 1" @click="loadList(store.list.page - 1)">上一页</button>
        <button class="btn" v-if="store.list.page < pages" @click="loadList(store.list.page + 1)">下一页</button>
      </div>
    </div>
  </section>`,
  computed: {
    pages() { return Math.ceil(store.list.total / store.list.size); },
  },
  methods: {
    onSearch: () => searchDebounced(),
    clearFilters() { store.filters.tag = ''; store.filters.category = ''; loadList(1); },
    openNote, loadList,
  },
  data: () => ({ store }),
};

const ReaderPane = {
  template: `
  <main class="reader">
    <div v-if="!store.current" class="reader-empty">
      <div class="big">📖</div><div>从中间挑一篇开始读</div>
    </div>
    <template v-else>
      <div class="reader-head">
        <h1>{{ store.current.title }}</h1>
        <div class="reader-ops">
          <button class="btn" @click="startEdit(store.current)">编辑</button>
          <button class="btn danger" @click="delNote(store.current.name)">删除</button>
        </div>
      </div>
      <div class="reader-meta">
        <span>{{ store.current.date }}</span>
        <span class="dot">{{ store.current.category }}</span>
        <span class="dot" v-for="t in store.current.tags" :key="t"><span class="chip">{{ t }}</span></span>
        <span class="dot" v-if="store.current.url">
          <a class="src-link" :href="store.current.url" target="_blank" rel="noopener">🔗 原文链接</a>
        </span>
        <span class="dot" v-if="store.current.raw_file">
          <a class="src-link" :href="'/api/raw/' + encodeURIComponent(store.current.raw_file)">📎 原始文件</a>
        </span>
      </div>
      <div class="reader-body">
        <div class="md" v-html="html"></div>
        <div class="related" v-if="store.current.related.length">
          <h4>相关笔记</h4>
          <div class="rel-grid">
            <div v-for="r in store.current.related" :key="r" class="rel-card" @click="openNote(r)">{{ r }}</div>
          </div>
        </div>
      </div>
    </template>
  </main>`,
  computed: {
    html() { return md(store.current?.body); },
  },
  methods: { startEdit, delNote, openNote },
  data: () => ({ store }),
};

const EditorPane = {
  template: `
  <main class="editor">
    <div class="editor-head">
      <input class="title" v-model="store.editing.title" placeholder="一句话说清这条资料的核心…">
      <div class="editor-row">
        <span class="lbl">分类</span>
        <select v-model="store.editing.category">
          <option v-for="c in store.categories" :key="c" :value="c">{{ c }}</option>
        </select>
        <span class="lbl">原文链接</span>
        <input class="url-input" v-model="store.editing.url" placeholder="https://…（可选）">
      </div>
      <div class="editor-row">
        <span class="lbl">标签</span>
        <span v-for="[t] in store.tagFreq" :key="t" class="chip" :class="{on: store.editing.tags.includes(t)}" @click="toggleTag(t)">{{ t }}</span>
      </div>
    </div>
    <div class="editor-main">
      <textarea v-model="store.editing.body" placeholder="正文（markdown）…"></textarea>
      <div class="preview"><div class="md" v-html="preview"></div></div>
    </div>
    <div class="editor-foot">
      <button class="btn" @click="store.view = 'reader'">取消</button>
      <button class="btn primary" @click="saveNote">保存</button>
    </div>
  </main>`,
  computed: {
    preview() { return md(store.editing.body); },
  },
  methods: {
    toggleTag(t) {
      const i = store.editing.tags.indexOf(t);
      i >= 0 ? store.editing.tags.splice(i, 1) : store.editing.tags.push(t);
    },
    saveNote,
  },
  data: () => ({ store }),
};

/* ---------- 根组件 ---------- */
const App = {
  components: { NavPane, ListPane, ReaderPane, EditorPane },
  template: `
  <div class="layout">
    <NavPane />
    <ListPane />
    <EditorPane v-if="store.view === 'editor'" />
    <ReaderPane v-else />
  </div>
  <div class="toast-wrap"><div v-for="t in store.toasts" :key="t.id" class="toast">{{ t.msg }}</div></div>`,
  data: () => ({ store }),
};

createApp(App).mount('#app');

/* 启动 */
(async () => {
  await refreshTags();
  await loadList(1);
})();
