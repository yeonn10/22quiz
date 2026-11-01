(function () {
  'use strict';
  var E = window.QuizEngine, DATA = window.QUIZ_DATA;
  var app = document.getElementById('app');
  var storage;
  try { storage = window.localStorage; storage.getItem('immuno22.probe'); }
  catch (e) { storage = { getItem: function () { return null; }, setItem: function () {} }; }   // 저장소 접근이 막힌 환경: 메모리만 사용
  var store = E.makeStore(storage);
  var qById = {}, order = new Map(), n = 0;
  DATA.questions.forEach(function (q) { qById[q.id] = q; order.set(q.id, n++); });
  var validIds = new Set(order.keys());
  var kindName = {}, unitName = {};
  DATA.kinds.forEach(function (k) { kindName[k.id] = k.name; });
  DATA.units.forEach(function (u) { unitName[u.id] = u.name; });

  var Q = null;        // 진행 중 퀴즈 상태
  var view = 'home';

  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function toast(msg) { var t = document.getElementById('toast'); t.textContent = msg; t.classList.add('show'); clearTimeout(toast.h); toast.h = setTimeout(function () { t.classList.remove('show'); }, 1600); }
  function updCount() { document.getElementById('bmCount').textContent = store.list().filter(function (i) { return validIds.has(i); }).length; }
  function srcText(s) { return s ? s.replace(/\s*,\s*/g, '·') + '학번' : ''; }

  /* ---------- 라우팅 ---------- */
  function go(h) { if (location.hash === h) route(); else location.hash = h; }
  function route() {
    app.className = '';
    var h = location.hash || '#/';
    if (h === '#/quiz' && Q) return quiz();
    if (h === '#/result' && Q) return result();
    if (h === '#/bookmarks') return bookmarks();
    if (h !== '#/') { location.hash = '#/'; return; }
    setup();
  }
  window.addEventListener('hashchange', route);

  /* ---------- 시작 화면(설정) ---------- */
  function setup() {
    view = 'setup'; updCount();
    var prefs = store.getPrefs().main || {};
    var allKinds = DATA.kinds.map(function (k) { return k.id; });
    var allUnits = DATA.units.map(function (u) { return u.id; });
    var kinds = (prefs.kinds || allKinds).filter(function (k) { return allKinds.indexOf(k) >= 0; });
    var units = (prefs.units || allUnits).filter(function (u) { return allUnits.indexOf(u) >= 0; });
    var shufQ = !!prefs.shuffle, shufO = !!prefs.shuffleOpts;
    function draw() {
      var uc = E.countUnits(DATA, kinds), kc = E.countKinds(DATA);
      var total = units.reduce(function (a, u) { return a + (kinds.length ? uc[u] : 0); }, 0);
      var bm = store.list().filter(function (i) { return validIds.has(i); }).length;
      app.innerHTML = '<h1>' + esc(DATA.title) + '</h1>' +
        '<div class="card"><h2>문제 유형</h2><div class="chips row">' + DATA.kinds.map(function (k) {
          return '<label><input type="checkbox" data-k="' + k.id + '"' + (kinds.indexOf(k.id) >= 0 ? ' checked' : '') + '>' + esc(k.name) + ' (' + kc[k.id] + ')</label>';
        }).join('') + '</div></div>' +
        '<div class="card"><div class="row"><h2 style="margin:0">단원</h2><button id="all">전체 선택</button><button id="none">전체 해제</button></div>' +
        '<div class="units">' + DATA.units.map(function (u) {
          return '<label class="chk"><input type="checkbox" data-u="' + u.id + '"' + (units.indexOf(u.id) >= 0 ? ' checked' : '') + '>' + esc(u.id + '. ' + u.name) + '<span class="n">' + uc[u.id] + '</span></label>';
        }).join('') + '</div></div>' +
        '<div class="card"><div class="row"><label class="chk"><input type="checkbox" id="shufq"' + (shufQ ? ' checked' : '') + '>문제 순서 섞기</label>' +
        '<label class="chk"><input type="checkbox" id="shufo"' + (shufO ? ' checked' : '') + '>객관식 보기 섞기 <small class="sub">(순서가 의미 있는 문항 제외)</small></label></div>' +
        '<div class="row" style="margin-top:8px"><span style="flex:1"></span><button id="bmgo"' + (bm ? '' : ' disabled') + '>★ 북마크만 풀기 (' + bm + ')</button>' +
        '<button class="primary" id="go"' + (total ? '' : ' disabled') + '>시작 (' + total + '문항)</button></div></div>' +
        '<p class="sub">정답은 「면역학 개론 기출문제 정리」(22·23학번 + 역대 모음) 표시 기준입니다. 북마크는 이 기기의 브라우저에 저장되며, 기기를 옮길 땐 북마크 화면의 내보내기/불러오기를 쓰세요.</p>';
      app.querySelectorAll('[data-k]').forEach(function (c) { c.onchange = function () { kinds = Array.from(app.querySelectorAll('[data-k]:checked')).map(function (x) { return x.dataset.k; }); draw(); }; });
      app.querySelectorAll('[data-u]').forEach(function (c) { c.onchange = function () { units = Array.from(app.querySelectorAll('[data-u]:checked')).map(function (x) { return x.dataset.u; }); draw(); }; });
      document.getElementById('all').onclick = function () { units = allUnits.slice(); draw(); };
      document.getElementById('none').onclick = function () { units = []; draw(); };
      document.getElementById('shufq').onchange = function (e) { shufQ = e.target.checked; };
      document.getElementById('shufo').onchange = function (e) { shufO = e.target.checked; };
      function remember() { var p = store.getPrefs(); p.main = { kinds: kinds, units: units, shuffle: shufQ, shuffleOpts: shufO }; store.setPrefs(p); }
      document.getElementById('go').onclick = function () {
        remember();
        start(E.buildDeck(DATA, { kinds: kinds, units: units, shuffle: shufQ }), '', shufO);
      };
      document.getElementById('bmgo').onclick = function () {
        remember();
        start(E.buildDeck(DATA, { onlyIds: store.list(), shuffle: shufQ }), '★ 북마크', shufO);
      };
    }
    draw();
  }

  function start(deck, label, shufO) {
    if (!deck.length) return toast('문제가 없습니다');
    if (shufO) deck = deck.map(function (q) { return E.shuffleOptions(q); });   // 보기는 시작할 때마다 새로 섞음
    Q = { deck: deck, i: 0, ans: {}, pend: [], txt: {}, label: label, shufO: !!shufO };
    go('#/quiz');
  }

  /* ---------- 퀴즈 ---------- */
  /* 북마크 옵션(새로고침 후에도 유지): 자동 저장(오답·모름 → 북마크) / 자동 해제(정답 → 북마크 해제). 기본 둘 다 꺼짐 */
  function getOpts() { var o = store.getPrefs()._opts || {}; return { save: !!o.save, del: !!o.del }; }
  function setOpt(k, v) { var p = store.getPrefs(); var o = p._opts || {}; o[k] = v; p._opts = o; store.setPrefs(p); }
  function cur() { return Q.deck[Q.i]; }

  function quiz() {
    view = 'quiz'; updCount();
    var q = cur(), a = Q.ans[q.id], done = !!a, isSA = q.kind === 'sa', multi = !isSA && q.ans.length > 1;
    var sel = (!isSA) ? (done ? a.sel : Q.pend) : [];
    var pct = Math.round(Object.keys(Q.ans).length / Q.deck.length * 100);
    var h = '<div class="qhead"><span><a href="#/">← 설정</a>' + (Q.label ? ' · ' + esc(Q.label) : '') + '</span><span>' + (Q.i + 1) + ' / ' + Q.deck.length + '</span></div>' +
      '<div class="bar"><i style="width:' + pct + '%"></i></div><div class="card">' +
      '<div class="qhead"><span><span class="tag">' + esc(kindName[q.kind] || q.kind) + '</span> ' + esc(unitName[q.unit] || q.unit) + (q.topic ? ' · ' + esc(q.topic) : '') +
      '</span><span>' + (q.src ? esc(srcText(q.src)) + ' · ' : '') + '<code>' + esc(q.no || q.id) + '</code> <button class="bm' + (store.has(q.id) ? ' on' : '') + '" id="bm" title="북마크 (B)">' + (store.has(q.id) ? '★' : '☆') + '</button></span></div>' +
      '<div class="qtext">' + esc(q.q) + (multi ? ' <span class="multi">(복수 선택)</span>' : '') + '</div>';
    var hasFig = !!q.fig;
    app.className = hasFig ? 'wide' : '';
    h += '<div class="qgrid' + (hasFig ? ' withfig' : '') + '">';
    if (hasFig) h += '<div class="figcol"><div class="fig"><img src="' + esc(q.fig) + '" alt="문제 그림"></div></div>';
    h += '<div class="optcol">';
    if (!isSA) {
      h += q.opts.map(function (o, i) {
        var no = i + 1, cls = '';
        if (done) { var isA = q.ans.indexOf(no) >= 0, isS = sel.indexOf(no) >= 0; cls = isA ? ' right' : (isS ? ' bad' : ''); }
        else if (sel.indexOf(no) >= 0) cls = ' sel';
        return '<button class="opt' + cls + '" data-o="' + no + '"><span class="no">' + E.label(i) + '</span><span>' + esc(o) + '</span></button>';
      }).join('');
      if (!done) h += '<div class="row"><button class="primary" id="submit">정답 확인 (Enter)</button></div>';
    } else {
      var typed = done ? (a.txt || '') : (Q.txt[q.id] || '');
      if (!done) {
        var hint = q.pool ? (q.anyof ? '하나만 입력' : '쉼표(,)로 구분해서 ' + q.need + '개 입력') : '정답 입력';
        h += '<input type="text" id="sa" class="sa" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" placeholder="' + esc(hint) + '" value="' + esc(typed) + '">' +
          '<div class="row"><button class="primary" id="submit">정답 확인 (Enter)</button></div>';
      } else if (!a.dk) {
        h += '<div class="myans">내 답: <b>' + (typed ? esc(typed) : '(빈칸)') + '</b></div>';
      }
    }
    if (done) {
      var bn = a.dk ? ['dk', '모름'] : a.correct ? ['ok', a.over ? '정답으로 인정 ✔' : '정답입니다 ✔'] : ['ng', '오답 ✘'];
      var ansLine;
      if (isSA) ansLine = ' — 정답: ' + E.answerText(q);
      else ansLine = a.correct ? '' : ' — 정답: ' + q.ans.map(function (x) { return E.label(x - 1); }).join(' ');
      h += '<div class="banner ' + bn[0] + '">' + bn[1] + esc(a.correct && !a.dk ? (isSA && q.pool && !a.over ? ' · ' + a.hit + '/' + q.need + '개 일치' + ansLine : ansLine) : ansLine) + '</div>';
      if (isSA && !a.dk) {
        if (q.pool && !a.over && a.hit !== undefined && !a.correct) h += '<div class="sub">일치한 항목 ' + a.hit + '개 / 필요 ' + q.need + '개</div>';
        h += '<div class="row"><button id="over">' + (a.correct ? '오답으로 처리' : '내 답도 맞게 인정') + '</button></div>';
      }
      if (q.exp) h += '<div class="exp">' + esc(q.exp) + '</div>';
    }
    h += '</div></div></div><div class="nav"><button id="prev"' + (Q.i ? '' : ' disabled') + '>← 이전</button>' +
      '<button id="dk"' + (done ? ' disabled' : '') + '>모름 (0)</button>' +
      '<button class="primary" id="next">' + (Q.i === Q.deck.length - 1 ? '결과 보기' : '다음 →') + '</button></div>' +
      '<div class="keys"><kbd>1</kbd>–<kbd>9</kbd> 선택 (10번 이상은 <kbd>1</kbd><kbd>2</kbd>처럼 빠르게 연속 입력) · <kbd>0</kbd> 모름 · <kbd>Enter</kbd> 정답 확인 및 다음 · <kbd>→</kbd>/<kbd>↓</kbd> 다음 · <kbd>←</kbd>/<kbd>↑</kbd> 이전 · <kbd>B</kbd> 북마크 · 주관식 입력 중에는 방향키·숫자키가 글자 입력에 쓰입니다</div>' +
      '<div class="bmopts"><label><input type="checkbox" id="optSave"' + (getOpts().save ? ' checked' : '') + '> 북마크 자동 저장 <small>(틀린 문제 자동 추가)</small></label>' +
      '<label><input type="checkbox" id="optDel"' + (getOpts().del ? ' checked' : '') + '> 북마크 자동 해제 <small>(맞힌 문제 자동 해제)</small></label></div>';
    app.innerHTML = h;
    app.querySelectorAll('.opt').forEach(function (b) { b.onclick = function () { b.blur(); pick(+b.dataset.o); }; });
    var sb = document.getElementById('submit'); if (sb) sb.onclick = function () { sb.blur(); submit(); };
    var si = document.getElementById('sa');
    if (si) { si.oninput = function () { Q.txt[q.id] = si.value; }; si.focus({ preventScroll: true }); }
    var ov = document.getElementById('over'); if (ov) ov.onclick = function (e) { e.target.blur(); override(); };
    document.getElementById('prev').onclick = function (e) { e.target.blur(); move(-1); };
    document.getElementById('next').onclick = function (e) { e.target.blur(); move(1); };
    document.getElementById('dk').onclick = function (e) { e.target.blur(); dontKnow(); };
    document.getElementById('bm').onclick = function (e) { e.target.blur(); toggleBm(); };
    document.getElementById('optSave').onchange = function (e) { setOpt('save', e.target.checked); e.target.blur(); };
    document.getElementById('optDel').onchange = function (e) { setOpt('del', e.target.checked); e.target.blur(); };
  }

  function afterGrade(q, ok) {
    var op = getOpts();
    if (!ok && op.save && store.add(q.id)) toast('★ 북마크에 자동 추가');
    else if (ok && op.del && store.remove(q.id)) toast('정답! 북마크에서 자동 해제');
  }
  function grade(sel, dk, txt) {
    var q = cur(); if (Q.ans[q.id]) return;
    var rec;
    if (q.kind === 'sa') {
      var g = dk ? { ok: false, hit: 0, need: q.need || 1 } : E.gradeShort(q, txt);
      rec = { txt: txt || '', dk: !!dk, correct: !!g.ok, hit: g.hit };
    } else {
      rec = { sel: sel.slice(), dk: !!dk, correct: !dk && E.isCorrect(q, sel) };
    }
    Q.ans[q.id] = rec;
    Q.pend = [];
    afterGrade(q, rec.correct);
    quiz();
  }
  /** 주관식: 자동 채점과 다르게 내가 직접 맞음/틀림을 바꿀 때 */
  function override() {
    var q = cur(), a = Q.ans[q.id]; if (!a || a.dk) return;
    a.correct = !a.correct; a.over = !a.over;
    afterGrade(q, a.correct);
    quiz();
  }
  function pick(no) {
    var q = cur(); if (q.kind === 'sa' || Q.ans[q.id] || no > q.opts.length || no < 1) return;
    if (q.ans.length === 1) Q.pend = (Q.pend[0] === no) ? [] : [no];   // 단일정답: 하나만 선택 (다시 누르면 해제)
    else { var i = Q.pend.indexOf(no); if (i >= 0) Q.pend.splice(i, 1); else Q.pend.push(no); }
    quiz();
  }
  function submit() {
    var q = cur(); if (Q.ans[q.id]) return;
    if (q.kind === 'sa') {
      var el = document.getElementById('sa'), v = el ? el.value : (Q.txt[q.id] || '');
      Q.txt[q.id] = v;
      if (!v.trim()) return toast('답을 입력하세요');
      grade([], false, v);
    } else if (Q.pend.length) grade(Q.pend, false);
    else toast('번호를 먼저 선택하세요');
  }
  function dontKnow() { var q = cur(); grade([], true, q.kind === 'sa' ? (Q.txt[q.id] || '') : undefined); }
  function toggleBm(force) {
    var q = cur(), has = store.has(q.id);
    if (force === 'add' || (force === undefined && !has)) { store.add(q.id); toast('★ 북마크 추가'); }
    else if (force === 'del' || has) { store.remove(q.id); toast('북마크 해제'); }
    quiz();
  }
  function move(d) {
    Q.pend = [];
    var ni = Q.i + d;
    if (ni < 0) return;
    if (ni >= Q.deck.length) return go('#/result');
    Q.i = ni; quiz();
  }

  /* 숫자 키: 보기가 10개 이상이면 짧은 시간 안에 이어 누른 숫자를 한 번호로 합친다 (예: 1 → 2 = 12번) */
  var numBuf = '', numTimer = null;
  function digit(d) {
    var q = cur();
    if (q.kind === 'sa') { if (d === '0') dontKnow(); return; }
    var len = q.opts.length;
    if (len < 10) { if (d === '0') dontKnow(); else pick(+d); return; }
    clearTimeout(numTimer);
    if (!numBuf && d === '0') { dontKnow(); return; }
    if (numBuf && +(numBuf + d) > len) numBuf = '';     // 범위를 넘으면 새로 시작
    numBuf += d;
    var v = +numBuf;
    if (v * 10 > len) { numBuf = ''; pick(v); }          // 더 이어 붙일 수 없으면 바로 확정
    else numTimer = setTimeout(function () { var x = +numBuf; numBuf = ''; pick(x); }, 550);
  }

  document.addEventListener('keydown', function (e) {
    if (view !== 'quiz' || !Q || e.ctrlKey || e.metaKey || e.altKey || e.isComposing) return;
    var t = e.target.tagName;
    if (t === 'INPUT' || t === 'TEXTAREA') {
      if (e.key === 'Enter' && e.target.id === 'sa') { e.preventDefault(); submit(); }
      return;
    }
    var k = e.key, handled = true;
    if (k >= '0' && k <= '9' && k.length === 1) digit(k);
    else if (k === 'b' || k === 'B' || k === 'ㅠ' || e.code === 'KeyB') toggleBm();   // 북마크 있으면 해제, 없으면 추가
    else if (k === 'Enter') { var q = cur(); if (Q.ans[q.id]) move(1); else submit(); }
    else if (k === 'ArrowRight' || k === 'ArrowDown') move(1);
    else if (k === 'ArrowLeft' || k === 'ArrowUp') move(-1);
    else handled = false;
    if (handled) e.preventDefault();
  });

  /* ---------- 결과 ---------- */
  function result() {
    view = 'result'; updCount();
    var s = E.summarize(Q.deck, Q.ans);
    app.innerHTML = '<h1>결과</h1><div class="card"><div class="stat">' +
      '<div><b>' + s.correct + '</b>정답</div><div><b>' + s.wrong + '</b>오답</div><div><b>' + s.dk + '</b>모름</div><div><b>' + s.skipped + '</b>안 푼 문제</div></div>' +
      '<p>' + s.total + '문항 중 ' + s.correct + '문항 정답 (' + Math.round(s.correct / s.total * 100) + '%).' + (getOpts().save ? ' 오답·모름은 자동으로 북마크되었습니다.' : '') + '</p>' +
      '<div class="row"><button id="back">마지막 문제로</button><button id="retry"' + (s.wrongIds.length ? '' : ' disabled') + '>틀린/모름 다시 풀기 (' + s.wrongIds.length + ')</button>' +
      '<button id="setup">설정으로</button></div></div>';
    document.getElementById('back').onclick = function () { go('#/quiz'); };
    document.getElementById('retry').onclick = function () { start(E.buildDeck(DATA, { onlyIds: s.wrongIds }), '틀린 문제 복습', Q.shufO); };
    document.getElementById('setup').onclick = function () { go('#/'); };
  }

  /* ---------- 북마크 ---------- */
  function bookmarks() {
    view = 'bookmarks'; updCount();
    var ids = E.sortIds(store.list(), order);
    var known = ids.filter(function (i) { return qById[i]; });
    var h = '<p><a href="#/">← 설정</a></p><h1>★ 북마크 (' + known.length + ')</h1><div class="card"><div class="row">' +
      '<button id="exp"' + (ids.length ? '' : ' disabled') + '>내보내기 (txt)</button>' +
      '<label class="btn">불러오기 (txt)<input type="file" id="file" accept=".txt,text/plain" hidden></label>' +
      '<label class="chk"><input type="checkbox" id="rep">기존 북마크 덮어쓰기</label><span style="flex:1"></span>' +
      '<button id="clr"' + (ids.length ? '' : ' disabled') + '>전체 삭제</button></div>' +
      '<p class="sub">내보낸 txt에는 문제 고유번호만 들어 있습니다. 다른 기기·브라우저에서 불러오기로 복원하세요.</p></div>';
    if (known.length) {
      h += '<div class="card"><div class="row"><span style="flex:1"></span><button class="primary" id="run">이 북마크만 풀기</button></div>' +
        known.map(function (i) {
          var q = qById[i];
          return '<div class="bmitem"><code>' + esc(q.no || i) + '</code><span>' + esc(q.q.replace(/\s+/g, ' ').slice(0, 90)) + '</span><button data-del="' + esc(i) + '">해제</button></div>';
        }).join('') + '</div>';
    } else h += '<p class="sub">북마크가 없습니다. 문제 화면의 ☆ 를 누르거나, 설정에서 “북마크 자동 저장”을 켜면 틀린 문제가 자동으로 들어옵니다.</p>';
    app.innerHTML = h;
    var run = document.getElementById('run');
    if (run) run.onclick = function () { start(E.buildDeck(DATA, { onlyIds: store.list() }), '★ 북마크', !!(store.getPrefs().main || {}).shuffleOpts); };
    app.querySelectorAll('[data-del]').forEach(function (b) { b.onclick = function () { store.remove(b.dataset.del); bookmarks(); }; });
    var ex = document.getElementById('exp'); if (ex) ex.onclick = exportTxt;
    document.getElementById('clr').onclick = function () { if (confirm('북마크를 모두 삭제할까요?')) { store.clear(); bookmarks(); } };
    document.getElementById('file').onchange = function (e) {
      var f = e.target.files[0]; if (!f) return;
      var r = new FileReader();
      r.onload = function () {
        var p = E.parseImport(String(r.result), validIds);
        if (!p.ids.length) return toast('복원할 유효한 번호가 없습니다' + (p.unknown.length ? ' (알 수 없는 ' + p.unknown.length + '개)' : ''));
        store.replace(E.mergeBookmarks(store.list(), p.ids, document.getElementById('rep').checked ? 'replace' : 'merge'));
        bookmarks();
        toast(p.ids.length + '개 복원' + (p.unknown.length ? ' · 알 수 없는 번호 ' + p.unknown.length + '개 무시' : ''));
      };
      r.readAsText(f, 'utf-8');
    };
  }
  function exportTxt() {
    var d = new Date(), p = function (x) { return (x < 10 ? '0' : '') + x; };
    var name = 'immuno_bookmarks_' + d.getFullYear() + p(d.getMonth() + 1) + p(d.getDate()) + '.txt';
    var blob = new Blob([E.formatExport(store.list(), order, d)], { type: 'text/plain;charset=utf-8' });
    var a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
    toast('내보냈습니다: ' + name);
  }

  route();
})();
