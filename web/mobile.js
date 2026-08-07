/* fuxi 知识库移动端：列表 / 详情 / 编辑 单页切换。兼容老内核，无 ES2020+ 语法。 */
(function () {
  var createApp = Vue.createApp;

  /* ---------- 工具 ---------- */
  function md(src) {
    return DOMPurify.sanitize(marked.parse(src || '', { breaks: true }));
  }
  function api(path, opts) {
    return fetch(path, opts).then(function (r) {
      if (!r.ok) {
        return r.json().catch(function () { return {}; }).then(function (d) {
          throw new Error(d.detail || r.statusText);
        });
      }
      return r.json();
    });
  }
  function debounce(fn, ms) {
    var t;
    return function () {
      var args = arguments, self = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(self, args); }, ms);
    };
  }

  /* ---------- 应用 ---------- */
  createApp({
    data: function () {
      return {
        view: 'list',           // list | detail | edit
        loading: true,
        categories: [], tagFreq: [], catCount: {}, tagZh: {},
        filters: { q: '', category: '', tag: '' },
        list: { items: [], total: 0, page: 1, size: 50 },
        current: null,
        editing: { name: '', title: '', category: 'misc', tags: [], body: '', raw_files: [], url: '' },
        newTag: '',
        toastMsg: '',
      };
    },
    computed: {
      pages: function () { return Math.ceil(this.list.total / this.list.size); },
      detailHtml: function () { return md(this.current ? this.current.body : ''); },
    },
    created: function () {
      this._search = debounce(this.loadList.bind(this, 1), 300);
      this.init();
    },
    methods: {
      init: function () {
        var self = this;
        api('/api/tags').then(function (d) {
          self.tagFreq = d.tags;
          self.categories = d.categories;
          self.catCount = d.cat_count || {};
          self.tagZh = d.tag_zh || {};
          return self.loadList(1);
        }).then(function () { self.loading = false; })
          .catch(function (e) { self.toast('加载失败：' + e.message); self.loading = false; });
      },
      toast: function (msg) {
        var self = this;
        self.toastMsg = msg;
        setTimeout(function () { self.toastMsg = ''; }, 2600);
      },
      tagLabel: function (t) {
        var zh = this.tagZh[t];
        return zh ? (t + '(' + zh + ')') : t;
      },
      onSearch: function () { this._search(); },
      loadList: function (page) {
        var self = this;
        self.list.page = page;
        var p = new URLSearchParams({ page: page, size: self.list.size });
        if (self.filters.q) p.set('q', self.filters.q);
        if (self.filters.category) p.set('category', self.filters.category);
        if (self.filters.tag) p.set('tag', self.filters.tag);
        return api('/api/notes?' + p).then(function (d) {
          self.list.items = d.items;
          self.list.total = d.total;
        });
      },
      clearFilters: function () {
        this.filters.tag = ''; this.filters.category = '';
        this.loadList(1);
      },
      openNote: function (name) {
        var self = this;
        api('/api/notes/' + encodeURIComponent(name)).then(function (n) {
          self.current = n;
          self.view = 'detail';
          window.scrollTo(0, 0);
        });
      },
      backToList: function () {
        this.view = 'list';
        this.current = null;
      },
      startEdit: function (note) {
        var n = note || {};
        this.editing = {
          name: n.name || '', title: n.title || '', category: n.category || 'misc',
          tags: (n.tags || []).slice(), body: n.body || '',
          raw_files: (n.raw_files || []).slice(), url: n.url || '',
        };
        this.view = 'edit';
        window.scrollTo(0, 0);
      },
      toggleTag: function (t) {
        var i = this.editing.tags.indexOf(t);
        if (i >= 0) this.editing.tags.splice(i, 1); else this.editing.tags.push(t);
      },
      addTag: function () {
        var t = this.newTag.trim();
        if (!t) return;
        if (this.editing.tags.indexOf(t) < 0) this.editing.tags.push(t);
        this.newTag = '';
      },
      suggestTags: function () {
        var self = this;
        var text = self.editing.title + '\n' + self.editing.body;
        if (!text.trim()) { self.toast('先写点正文'); return; }
        self.toast('分析中…');
        api('/api/suggest_tags', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: text }),
        }).then(function (d) {
          // 推荐的标签合并进已选（不覆盖用户手选的）
          d.tags.forEach(function (t) {
            if (self.editing.tags.indexOf(t) < 0) self.editing.tags.push(t);
          });
          // 分类只在用户没改过时（还是默认 misc）才自动填
          if (self.editing.category === 'misc' && d.category !== 'misc') {
            self.editing.category = d.category;
          }
          self.toast(d.tags.length ? '推荐了 ' + d.tags.length + ' 个标签' : '没匹配到已有标签');
        }).catch(function (e) { self.toast('推荐失败：' + e.message); });
      },
      saveNote: function () {
        var self = this;
        if (!self.editing.title.trim()) { self.toast('标题不能为空'); return; }
        api('/api/notes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(self.editing),
        }).then(function (r) {
          self.toast('已保存');
          return self.loadList(self.list.page).then(function () { return self.openNote(r.name); });
        }).catch(function (e) { self.toast('保存失败：' + e.message); });
      },
      delNote: function (name) {
        var self = this;
        if (!confirm('删除后移入 trash/（不真删），确定？')) return;
        api('/api/notes/' + encodeURIComponent(name), { method: 'DELETE' }).then(function () {
          self.toast('已移入 trash/');
          self.backToList();
          return self.loadList(1);
        });
      },
      promptUrl: function () {
        var url = prompt('粘贴原文链接（正文先贴到笔记里，抓取管线二期再做）：');
        this.startEdit({ url: (url || '').trim() });
      },
      uploadFiles: function (ev) {
        var self = this;
        var files = ev.target.files;
        if (!files || !files.length) return;
        var fd = new FormData();
        for (var i = 0; i < files.length; i++) fd.append('files', files[i]);
        self.toast('转换中…');
        api('/api/upload', { method: 'POST', body: fd }).then(function (r) {
          var ok = r.files.filter(function (f) { return !f.error; });
          var fail = r.files.filter(function (f) { return f.error; });
          if (!ok.length) { self.toast('全部失败：' + ((fail[0] && fail[0].error) || '未知')); return; }
          var body = ok.map(function (f) { return f.text; }).join('\n\n---\n\n');
          var raw_files = ok.map(function (f) { return f.raw_file; });
          var title = ok[0].raw_file.replace(/^\d{4}-\d{2}-\d{2}-/, '').replace(/\.[^.]+$/, '');
          self.startEdit({ title: title, body: body, raw_files: raw_files });
          self.toast(fail.length ? (ok.length + ' 个成功，' + fail.length + ' 个失败') : ('已存 ' + ok.length + ' 个文件'));
        }).catch(function (e) { self.toast('上传失败：' + e.message); });
        ev.target.value = '';
      },
      shortName: function (f) {
        var base = f.replace(/^\d{4}-\d{2}-\d{2}-/, '');
        return base.length > 20 ? base.slice(0, 20) + '…' : base;
      },
    },
    template: [
      '<div v-if="loading" class="loading">加载中…</div>',

      /* 列表 */
      '<div v-else-if="view === \'list\'">',
      '  <div class="topbar">',
      '    <h1>fuxi</h1><span class="sub">知识库</span>',
      '    <div class="actions">',
      '      <button class="btn primary" @click="startEdit()">＋ 记笔记</button>',
      '      <button class="btn" @click="promptUrl">🔗 丢链接</button>',
      '      <button class="btn" @click="$refs.file.click()">上传</button>',
      '      <input type="file" ref="file" hidden multiple @change="uploadFiles">',
      '    </div>',
      '    <div class="search-row"><input type="search" v-model="filters.q" placeholder="全文搜索…" @input="onSearch"></div>',
      '    <div class="filters">',
      '      <select v-model="filters.category" @change="loadList(1)">',
      '        <option value="">全部分类</option>',
      '        <option v-for="c in categories" :key="c" :value="c">{{ c }} ({{ catCount[c] || 0 }})</option>',
      '      </select>',
      '      <select v-model="filters.tag" @change="loadList(1)">',
      '        <option value="">全部标签</option>',
      '        <option v-for="tg in tagFreq" :key="tg[0]" :value="tg[0]">{{ tagLabel(tg[0]) }} ({{ tg[1] }})</option>',
      '      </select>',
      '    </div>',
      '  </div>',
      '  <div class="count">共 {{ list.total }} 篇<span v-if="pages > 1">，第 {{ list.page }}/{{ pages }} 页</span>',
      '    <a v-if="filters.tag || filters.category" href="javascript:;" style="margin-left:10px" @click="clearFilters">清除筛选 ✕</a></div>',
      '  <div class="list">',
      '    <div v-if="!list.items.length" class="empty">没有匹配的笔记</div>',
      '    <div v-for="n in list.items" :key="n.name" class="note-card" @click="openNote(n.name)">',
      '      <h3>{{ n.title }}</h3>',
      '      <div class="meta">{{ n.date }}<span class="cat">{{ n.category }}</span></div>',
      '      <div class="tags" v-if="n.tags.length"><span v-for="t in n.tags" :key="t" class="chip">{{ t }}</span></div>',
      '    </div>',
      '    <div class="pager" v-if="pages > 1">',
      '      <button class="btn" v-if="list.page > 1" @click="loadList(list.page - 1)">上一页</button>',
      '      <button class="btn" v-if="list.page < pages" @click="loadList(list.page + 1)">下一页</button>',
      '    </div>',
      '  </div>',
      '</div>',

      /* 详情 */
      '<div v-else-if="view === \'detail\' && current" class="detail">',
      '  <div class="detail-bar">',
      '    <span class="back" @click="backToList">← 返回</span>',
      '    <span class="spacer"></span>',
      '    <button class="btn" @click="startEdit(current)">编辑</button>',
      '    <button class="btn danger" @click="delNote(current.name)">删除</button>',
      '  </div>',
      '  <div class="detail-head"><h1>{{ current.title }}</h1></div>',
      '  <div class="detail-meta">',
      '    <span>{{ current.date }}</span><span>·</span><span>{{ current.category }}</span>',
      '    <span v-for="t in current.tags" :key="t" class="chip">{{ t }}</span>',
      '    <a v-if="current.url" class="src-link" :href="current.url" target="_blank" rel="noopener">🔗 原文链接</a>',
      '    <a v-for="rf in current.raw_files" :key="rf" class="src-link" :href="\'/api/raw/\' + encodeURIComponent(rf)">📎 {{ shortName(rf) }}</a>',
      '  </div>',
      '  <div class="detail-body">',
      '    <div class="md" v-html="detailHtml"></div>',
      '    <div class="related" v-if="current.related.length">',
      '      <h4>相关笔记</h4>',
      '      <div v-for="r in current.related" :key="r" class="rel-card" @click="openNote(r)">{{ r }}</div>',
      '    </div>',
      '  </div>',
      '</div>',

      /* 编辑 */
      '<div v-else-if="view === \'edit\'" class="editor">',
      '  <div class="editor-bar">',
      '    <span class="back" @click="view = current ? \'detail\' : \'list\'">← 取消</span>',
      '    <span class="spacer"></span>',
      '    <button class="btn primary" @click="saveNote">保存</button>',
      '  </div>',
      '  <div class="editor-form">',
      '    <div class="f-row"><label>标题</label><input type="text" v-model="editing.title" placeholder="一句话说清核心"></div>',
      '    <div class="f-row"><label>分类</label>',
      '      <select v-model="editing.category" style="width:100%;padding:9px;border:1px solid var(--line);border-radius:8px;background:var(--bg)">',
      '        <option v-for="c in categories" :key="c" :value="c">{{ c }}</option></select></div>',
      '    <div class="f-row"><label>原文链接（可选）</label><input type="text" v-model="editing.url" placeholder="https://…"></div>',
      '    <div class="f-row"><label>标签 <a href="javascript:;" style="color:var(--accent);font-weight:400" @click="suggestTags">✨ 智能推荐</a></label>',
      '      <div class="tag-pick">',
      '        <span v-for="tg in tagFreq" :key="tg[0]" class="chip" :class="{on: editing.tags.indexOf(tg[0]) >= 0}" @click="toggleTag(tg[0])">{{ tagLabel(tg[0]) }}</span>',
      '        <input class="tag-input" v-model="newTag" placeholder="＋新标签，回车" @keydown.enter.prevent="addTag">',
      '      </div></div>',
      '    <div class="f-row"><label>正文（markdown）</label><textarea v-model="editing.body"></textarea></div>',
      '  </div>',
      '</div>',

      '<div v-if="toastMsg" class="toast">{{ toastMsg }}</div>',
    ].join('\n'),
  }).mount('#app');
})();
