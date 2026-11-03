(() => {
  'use strict';

  const app = document.getElementById('app');
  const deckCache = new Map();
  const miniScaler = new WeakMap();
  let indexData = null;

  /* ---------------- utils ---------------- */
  const $ = (sel, root = document) => root.querySelector(sel);

  function toast(msg) {
    let t = $('.toast');
    if (!t) {
      t = document.createElement('div');
      t.className = 'toast';
      document.body.appendChild(t);
    }
    t.textContent = msg;
    requestAnimationFrame(() => t.classList.add('show'));
    clearTimeout(t._timer);
    t._timer = setTimeout(() => t.classList.remove('show'), 1800);
  }

  async function loadIndex() {
    if (indexData) return indexData;
    const res = await fetch('data/index.json', { cache: 'no-cache' });
    indexData = await res.json();
    return indexData;
  }

  async function loadDeck(id) {
    if (deckCache.has(id)) return deckCache.get(id);
    const res = await fetch(`data/decks/${id}.json`);
    if (!res.ok) throw new Error('课件加载失败：' + id);
    const data = await res.json();
    deckCache.set(id, data);
    return data;
  }

  /* ---------------- slide renderer ---------------- */
  function buildTable(n) {
    const tb = n.tb;
    const table = document.createElement('table');
    table.className = 'tbl';
    table.setAttribute('style', n.s || '');
    const tbody = document.createElement('tbody');
    tb.rows.forEach((row) => {
      const tr = document.createElement('tr');
      row.forEach((cell) => {
        const td = document.createElement('td');
        td.setAttribute('style', [tb.bc, cell.cs].filter(Boolean).join(';'));
        const inner = document.createElement('div');
        inner.setAttribute('style', [tb.bt, cell.s].filter(Boolean).join(';'));
        inner.textContent = cell.x;
        td.appendChild(inner);
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    return table;
  }

  function build(n) {
    if (typeof n === 'string') return document.createTextNode(n);
    let el;
    switch (n.t) {
      case 'Slide':
        el = document.createElement('div');
        el.className = 'slide';
        break;
      case 'Image':
        el = document.createElement('img');
        el.alt = '';
        el.draggable = false;
        el.src = n.a.src;
        break;
      case 'Table':
        el = buildTable(n);
        break;
      case 'span':
        el = document.createElement('span');
        break;
      case 'br':
        el = document.createElement('br');
        break;
      default:
        el = document.createElement('div');
    }
    if (n.s) el.setAttribute('style', n.s);
    if (n.c && n.c.length) n.c.forEach((c) => el.appendChild(build(c)));
    return el;
  }

  function scaleMini(container, slide) {
    const s = container.clientWidth / 1280;
    slide.style.transform = `scale(${s})`;
  }

  /* ---------------- hub ---------------- */
  const state = { week: 'ALL', q: '' };

  function icon(name, size = 15) {
    const paths = {
      search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.2-3.2"/>',
      back: '<path d="M15 18l-6-6 6-6"/>',
      grid: '<rect x="3" y="3" width="7" height="7" rx="1.4"/><rect x="14" y="3" width="7" height="7" rx="1.4"/><rect x="3" y="14" width="7" height="7" rx="1.4"/><rect x="14" y="14" width="7" height="7" rx="1.4"/>',
      link: '<path d="M10 13a5 5 0 0 0 7.1 0l2-2a5 5 0 0 0-7.1-7.1L11 5"/><path d="M14 11a5 5 0 0 0-7.1 0l-2 2a5 5 0 0 0 7.1 7.1L13 19"/>',
      full: '<path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M16 3h3a2 2 0 0 1 2 2v3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/><path d="M8 21H5a2 2 0 0 1-2-2v-3"/>',
      close: '<path d="M18 6 6 18M6 6l12 12"/>',
      arrow: '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
    };
    return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${paths[name] || ''}</svg>`;
  }

  function cardHtml(d) {
    return `
      <article class="card" data-id="${d.id}" tabindex="0" role="button" aria-label="${d.id} ${escapeAttr(d.title)}">
        <div class="thumb">
          <div class="thumb-skel"></div>
          <div class="mini" data-deck="${d.id}"></div>
          <span class="badge-week">${d.id}</span>
          <span class="badge-pages">${d.pages} 页</span>
        </div>
        <div class="card-body">
          <div class="card-title">${escapeHtml(d.title)}</div>
          <div class="card-foot">
            第 ${d.week.slice(1)} 周 · 第 ${d.day.slice(1)} 讲
            <span class="arrow">${icon('arrow', 14)}</span>
          </div>
        </div>
      </article>`;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  }
  const escapeAttr = escapeHtml;

  function renderHub() {
    document.body.classList.remove('in-viewer');
    document.title = 'AI 产品经理实战训练营 · 课件在线版';
    const data = indexData;
    const weeks = [...new Set(data.decks.map((d) => d.week))];
    const totalPages = data.decks.reduce((s, d) => s + d.pages, 0);

    app.innerHTML = `
      <header class="topbar">
        <div class="brand">
          <span class="brand-mark">AI</span>
          <span class="brand-text">课程课件库 <span>· 在线放映版</span></span>
        </div>
        <div class="topbar-right">
          <span class="top-link top-count">共 ${data.decks.length} 讲 · ${totalPages} 页</span>
          <a class="top-link back-kit" href="../index.html">← 资源包</a>
        </div>
      </header>
      <main class="wrap">
        <section class="hero">
          <span class="eyebrow"><i></i>AI 产品经理实战训练营 · 8 周</span>
          <h1 class="hero-title">课件在线版，<em>点开就能讲</em></h1>
          <p class="hero-sub">全部 ${data.decks.length} 讲课件已按原始版式转为网页放映版。点击任意一讲即可全屏播放，支持方向键翻页、手机横屏与单页链接分享。</p>
          <div class="stats">
            <div class="stat p"><b>8</b><span>周课程</span></div>
            <div class="stat"><b>${data.decks.length}</b><span>讲课件</span></div>
            <div class="stat b"><b>${totalPages}</b><span>页幻灯片</span></div>
          </div>
        </section>

        <section class="toolbar">
          <label class="search">
            ${icon('search', 15)}
            <input type="search" placeholder="搜索课程，如「RAG」「简历」" value="${escapeAttr(state.q)}" />
          </label>
          <div class="weeks">
            <button class="chip ${state.week === 'ALL' ? 'on' : ''}" data-week="ALL">全部</button>
            ${weeks.map((w) => `<button class="chip ${state.week === w ? 'on' : ''}" data-week="${w}">${w}</button>`).join('')}
          </div>
          <span class="count-note" id="count-note"></span>
        </section>

        <section class="grid" id="grid"></section>
        <div class="empty" id="empty" hidden>没有匹配的课程，换个关键词试试。</div>

        <footer class="footer">
          <span>AI 产品经理实战训练营 · 讲师 张小培</span>
          <span>数据生成于 ${data.generated} · 与本地 PPT 成品同源</span>
        </footer>
      </main>`;

    applyFilter();

    $('.search input').addEventListener('input', (e) => {
      state.q = e.target.value.trim();
      applyFilter();
    });
    document.querySelectorAll('.chip').forEach((b) => {
      b.addEventListener('click', () => {
        state.week = b.dataset.week;
        document.querySelectorAll('.chip').forEach((x) => x.classList.toggle('on', x === b));
        applyFilter();
      });
    });
  }

  function applyFilter() {
    const grid = $('#grid');
    if (!grid) return;
    const q = state.q.toLowerCase();
    const list = indexData.decks.filter((d) => {
      const okWeek = state.week === 'ALL' || d.week === state.week;
      const okQ = !q || (d.title + d.id).toLowerCase().includes(q);
      return okWeek && okQ;
    });
    grid.innerHTML = list.map(cardHtml).join('');
    $('#empty').hidden = list.length > 0;
    const note = $('#count-note');
    if (note) note.textContent = `${list.length} 讲 / ${list.reduce((s, d) => s + d.pages, 0)} 页`;

    grid.querySelectorAll('.card').forEach((card) => {
      const go = () => { location.hash = `#/deck/${card.dataset.id}`; };
      card.addEventListener('click', go);
      card.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); } });
    });
    observeThumbs();
  }

  let observer = null;
  function observeThumbs() {
    if (observer) observer.disconnect();
    observer = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (!en.isIntersecting) return;
        observer.unobserve(en.target);
        const box = en.target;
        const id = box.dataset.deck;
        loadDeck(id)
          .then((deck) => {
            if (!box.isConnected) return;
            box.innerHTML = '';
            const slide = build(deck.slides[0]);
            slide.style.transformOrigin = 'top left';
            box.appendChild(slide);
            const scaler = () => { if (box.clientWidth) scaleMini(box, slide); };
            scaler();
            miniScaler.set(box, scaler);
            const skel = box.parentElement.querySelector('.thumb-skel');
            if (skel) skel.remove();
          })
          .catch(() => {});
      });
    }, { rootMargin: '300px 0px' });
    document.querySelectorAll('.mini').forEach((m) => observer.observe(m));
  }

  window.addEventListener('resize', () => {
    document.querySelectorAll('.mini').forEach((m) => {
      const fn = miniScaler.get(m);
      if (fn) fn();
    });
  });

  /* ---------------- viewer ---------------- */
  let viewer = null;

  async function openDeck(id, page) {
    let deck;
    try {
      deck = await loadDeck(id);
    } catch (e) {
      toast('课件加载失败，请检查网络');
      location.hash = '';
      return;
    }
    const meta = indexData.decks.find((d) => d.id === id);
    const total = deck.slides.length;
    let idx = Math.min(Math.max((page || 1) - 1, 0), total - 1);

    document.body.classList.add('in-viewer');
    document.title = `${meta ? meta.title : id} · 课件在线版`;
    app.innerHTML = `
      <div class="viewer">
        <div class="v-top">
          <button class="icon-btn" id="v-back">${icon('back', 15)}<span>目录</span></button>
          <div class="v-title">
            <b>${escapeHtml(meta ? meta.title : id)}</b>
            <span>${id} · ${total} 页</span>
          </div>
          <div class="v-tools">
            <span class="v-page" id="v-page">1 / ${total}</span>
            <button class="icon-btn" id="v-thumbs">${icon('grid', 15)}<span>缩略图</span></button>
            <button class="icon-btn share" id="v-share">${icon('link', 15)}<span>复制链接</span></button>
            <button class="icon-btn" id="v-full">${icon('full', 15)}<span>全屏</span></button>
          </div>
        </div>
        <div class="v-stage" id="v-stage">
          <div class="v-zone left" id="v-prev"></div>
          <div class="v-zone right" id="v-next"></div>
          <div class="v-hint" id="v-hint">左右滑动翻页 · 横屏更清晰</div>
        </div>
        <div class="v-progress"><i id="v-bar"></i></div>
      </div>`;

    const stage = $('#v-stage');
    let slideEl = null;

    const paint = () => {
      if (slideEl) slideEl.remove();
      slideEl = build(deck.slides[idx]);
      slideEl.style.transformOrigin = 'top left';
      stage.appendChild(slideEl);
      fit();
      $('#v-page').textContent = `${idx + 1} / ${total}`;
      $('#v-bar').style.width = `${((idx + 1) / total) * 100}%`;
    };

    const fit = () => {
      if (!slideEl) return;
      const w = stage.clientWidth;
      const h = stage.clientHeight;
      const pad = w > 720 ? 30 : 8;
      const s = Math.min((w - pad * 2) / 1280, (h - pad * 2) / 720);
      slideEl.style.transform = `scale(${s})`;
      slideEl.style.left = `${(w - 1280 * s) / 2}px`;
      slideEl.style.top = `${(h - 720 * s) / 2}px`;
    };

    const go = (next) => {
      const n = Math.min(Math.max(next, 0), total - 1);
      if (n === idx) return;
      idx = n;
      paint();
      history.replaceState(null, '', `#/deck/${id}/${idx + 1}`);
      if (typeof sheet !== 'undefined' && sheet) markThumb();
    };

    viewer = {
      id,
      total,
      onKey(e) {
        if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') { e.preventDefault(); go(idx + 1); }
        else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); go(idx - 1); }
        else if (e.key === 'Home') { go(0); }
        else if (e.key === 'End') { go(total - 1); }
        else if (e.key === 'Escape') { closeOverlays(); }
        else if (e.key.toLowerCase() === 'g') { openThumbs(); }
      },
      destroy() { viewer = null; },
    };

    paint();

    $('#v-prev').addEventListener('click', () => go(idx - 1));
    $('#v-next').addEventListener('click', () => go(idx + 1));
    $('#v-back').addEventListener('click', () => { location.hash = ''; });
    $('#v-thumbs').addEventListener('click', openThumbs);
    $('#v-share').addEventListener('click', () => {
      copyLink(`${location.origin}${location.pathname}#/deck/${id}/${idx + 1}`);
    });
    $('#v-full').addEventListener('click', () => {
      if (document.fullscreenElement) document.exitFullscreen();
      else document.documentElement.requestFullscreen?.().catch(() => {});
    });

    const hint = $('#v-hint');
    if (hint) setTimeout(() => hint.classList.add('gone'), 3600);

    const rt = new ResizeObserver(() => fit());
    rt.observe(stage);

    // touch swipe
    let sx = 0, sy = 0, moved = false;
    stage.addEventListener('touchstart', (e) => {
      sx = e.touches[0].clientX; sy = e.touches[0].clientY; moved = false;
    }, { passive: true });
    stage.addEventListener('touchmove', () => { moved = true; }, { passive: true });
    stage.addEventListener('touchend', (e) => {
      const dx = e.changedTouches[0].clientX - sx;
      const dy = e.changedTouches[0].clientY - sy;
      if (!moved || Math.abs(dx) < 40 || Math.abs(dy) > 80) return;
      go(dx < 0 ? idx + 1 : idx - 1);
    }, { passive: true });
  }

  function copyLink(url) {
    const done = () => toast('链接已复制，可直接分享');
    if (navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(url).then(done).catch(() => fallbackCopy(url, done));
    } else fallbackCopy(url, done);
  }
  function fallbackCopy(url, cb) {
    const ta = document.createElement('textarea');
    ta.value = url;
    ta.style.cssText = 'position:fixed;opacity:0;top:0;left:0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); cb(); } catch (e) { toast('复制失败，请手动复制地址栏'); }
    ta.remove();
  }

  /* ---------------- thumbnails ---------------- */
  let sheet = null;

  function closeOverlays() {
    if (sheet) { sheet.remove(); sheet = null; }
  }

  function openThumbs() {
    if (!viewer) return;
    if (sheet) { closeOverlays(); return; }
    const deck = deckCache.get(viewer.id);
    if (!deck) return;
    const meta = indexData.decks.find((d) => d.id === viewer.id);

    sheet = document.createElement('div');
    sheet.className = 'sheet';
    sheet.innerHTML = `
      <div class="sheet-head">
        <b>${escapeHtml(meta ? meta.title : viewer.id)}</b>
        <span class="n">${deck.slides.length} 页 · 点击跳转</span>
        <button class="icon-btn" id="s-close" style="margin-left:auto">${icon('close', 15)}<span>关闭</span></button>
      </div>
      <div class="sheet-body"><div class="sheet-grid" id="s-grid"></div></div>`;
    document.body.appendChild(sheet);

    const grid = $('#s-grid', sheet);
    deck.slides.forEach((s, i) => {
      const cell = document.createElement('div');
      cell.className = 'thumb-cell';
      cell.dataset.i = i;
      cell.innerHTML = `<div class="thumb-frame"><div class="mini"></div></div><div class="thumb-num"><span>${String(i + 1).padStart(2, '0')}</span><span>${i === 0 ? '封面' : ''}</span></div>`;
      grid.appendChild(cell);
      const box = $('.mini', cell);
      const el = build(s);
      el.style.transformOrigin = 'top left';
      box.appendChild(el);
      requestAnimationFrame(() => scaleMini(box, el));
      cell.addEventListener('click', () => {
        closeOverlays();
        const target = Number(cell.dataset.i);
        if (target === Number($('#v-page').textContent.split('/')[0]) - 1) return;
        jumpTo(target);
      });
    });
    markThumb();
    $('#s-close', sheet).addEventListener('click', closeOverlays);
    const active = $('.thumb-cell.on', sheet);
    if (active) active.scrollIntoView({ block: 'center' });
  }

  function markThumb() {
    if (!sheet) return;
    const cur = Number($('#v-page').textContent.split('/')[0]) - 1;
    sheet.querySelectorAll('.thumb-cell').forEach((c) => c.classList.toggle('on', Number(c.dataset.i) === cur));
  }

  function jumpTo(target) {
    // reuse the arrow-key path via a synthetic click on the next zone is fiddly; dispatch a key instead
    const times = Math.abs(target - (Number($('#v-page').textContent.split('/')[0]) - 1));
    const key = target > Number($('#v-page').textContent.split('/')[0]) - 1 ? 'ArrowRight' : 'ArrowLeft';
    for (let i = 0; i < times; i++) {
      document.dispatchEvent(new KeyboardEvent('keydown', { key }));
    }
  }

  /* ---------------- router ---------------- */
  function route() {
    closeOverlays();
    const raw = location.hash.replace(/^#\/?/, '');
    const parts = raw.split('/');
    if (parts[0] === 'deck' && parts[1]) {
      openDeck(parts[1], Number(parts[2] || 1));
    } else {
      if (viewer) viewer.destroy();
      renderHub();
      window.scrollTo({ top: 0 });
    }
  }

  document.addEventListener('keydown', (e) => {
    if (sheet && e.key === 'Escape') { closeOverlays(); return; }
    if (viewer) viewer.onKey(e);
  });

  window.addEventListener('hashchange', route);

  loadIndex()
    .then(() => route())
    .catch(() => {
      app.innerHTML = '<div class="wrap"><p style="padding:80px 0;text-align:center;color:#6B6880">数据加载失败，请刷新重试。</p></div>';
    });
})();
