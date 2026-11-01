/* 퀴즈 엔진: 화면과 무관한 순수 로직 (채점, 덱 만들기, 북마크 저장/내보내기/복원) */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.QuizEngine = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // 22midterm 사이트와 같은 주소(yeonn10.github.io)를 쓰므로 저장 키가 겹치지 않게 따로 둔다
  var BOOKMARK_KEY = 'immuno22.bookmarks.v1';
  var PREF_KEY = 'immuno22.prefs.v1';
  var CIRCLED = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩', '⑪', '⑫', '⑬', '⑭', '⑮', '⑯', '⑰', '⑱', '⑲', '⑳'];

  function label(i) { return i < CIRCLED.length ? CIRCLED[i] : String(i + 1); }

  /* ---------- 객관식 채점 ---------- */
  /** 선택한 번호(1부터)가 정답 집합과 정확히 같은지 */
  function isCorrect(q, selected) {
    var a = q.ans.slice().sort(function (x, y) { return x - y; }).join(',');
    var s = Array.from(new Set(selected)).sort(function (x, y) { return x - y; }).join(',');
    return a === s;
  }

  /* ---------- 주관식 채점 ---------- */
  /** 비교용 정규화: 소문자, 영문·숫자·한글·그리스 문자만 남김 (띄어쓰기·하이픈·괄호 무시) */
  function norm(s) {
    return String(s == null ? '' : s).toLowerCase().replace(/[^0-9a-zㄱ-ㆎ가-힣α-ω]+/g, '');
  }

  /** 나열형 입력을 항목으로 쪼갬 (쉼표·세미콜론·줄바꿈·슬래시·' and ') */
  function splitItems(text) {
    return String(text || '').split(/[,;\n\/、，]+|\s+and\s+/i).map(function (t) { return t.trim(); }).filter(Boolean);
  }

  /** 주관식 채점. 돌려주는 값: { ok, hit, need } (단답형은 need=1) */
  function gradeShort(q, text) {
    if (q.pool) {
      var used = {}, hit = 0;
      splitItems(text).forEach(function (tok) {
        var n = norm(tok);
        if (!n) return;
        for (var i = 0; i < q.pool.length; i++) {
          if (used[i]) continue;
          if (q.pool[i].a.some(function (v) { return norm(v) === n; })) { used[i] = 1; hit++; return; }
        }
      });
      return { ok: hit >= q.need, hit: hit, need: q.need };
    }
    var n2 = norm(text);
    var ok = !!n2 && (q.acc || []).some(function (v) { return norm(v) === n2; });
    return { ok: ok, hit: ok ? 1 : 0, need: 1 };
  }

  /** 정답 안내 문구 */
  function answerText(q) {
    if (q.pool) {
      var list = q.pool.map(function (p) { return p.s; }).join(', ');
      if (q.anyof) return list + ' 중 하나';
      if (q.need < q.pool.length) return list + ' 중 ' + q.need + '개';
      return list;
    }
    return q.show;
  }

  /* ---------- 섞기 ---------- */
  function shuffle(arr, rng) {
    rng = rng || Math.random;
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(rng() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  var PIN_RE = /^\s*(정답\s*없음|해당\s*없음|모두\s*(옳|맞|정답|해당|아니)|위의?\s*(보기\s*)?(모두|중\s*없)|all of the above|none of the above|none\b)/i;
  var LABEL_RE = /^\s*[\(（]?([가-하]|[ㄱ-ㅎ]|[A-Ja-j])[\)）\.]?\s*$/;
  var NUMTOK = /[-+−]?\d+(?:[.,]\d+)?/g;

  /** 보기 순서가 의미를 갖는 문항은 섞지 않는다 (묶음 문항·그림 참조·가나다·연속 숫자·① 지칭 등) */
  function isFixedOrder(q) {
    if (q.fixed || q.kind !== 'mc') return true;
    var o = q.opts;
    if (o.length < 2) return true;
    if (o.every(function (x) { return LABEL_RE.test(x); })) return true;
    if (o.some(function (x) { return /[①-⑳]/.test(x); })) return true;
    if (o.every(function (x) { return /\d/.test(x); })) {
      var shape = o.map(function (x) { return x.replace(NUMTOK, '#').replace(/\s+/g, ''); });
      if (shape.every(function (t) { return t === shape[0]; })) return true;
    }
    if (/[①-⑳]|[1-9]\d{0,2}\s*번/.test(q.exp || '')) return true;
    return false;
  }

  /** 보기를 섞은 새 문항을 돌려준다. 'None' 류는 맨 뒤에 고정. 원본은 건드리지 않는다 */
  function shuffleOptions(q, rng) {
    if (isFixedOrder(q)) return q;
    var idx = q.opts.map(function (_, i) { return i; });
    var free = idx.filter(function (i) { return !PIN_RE.test(q.opts[i]); });
    var pinned = idx.filter(function (i) { return PIN_RE.test(q.opts[i]); });
    var order = shuffle(free, rng).concat(pinned);   // order[newPos] = oldIndex
    var copy = {};
    for (var k in q) copy[k] = q[k];
    copy.opts = order.map(function (i) { return q.opts[i]; });
    copy.ans = q.ans.map(function (a) { return order.indexOf(a - 1) + 1; }).sort(function (x, y) { return x - y; });
    return copy;
  }

  /* ---------- 덱 ---------- */
  /** 유형/단원 필터로 문제 덱 만들기. 순서는 단원 → 원래 순서 */
  function buildDeck(data, opt) {
    opt = opt || {};
    var kinds = opt.kinds || data.kinds.map(function (k) { return k.id; });
    var units = opt.units || data.units.map(function (u) { return u.id; });
    var only = opt.onlyIds ? new Set(opt.onlyIds) : null;
    var uo = {}; data.units.forEach(function (u, i) { uo[u.id] = i; });
    var idx = {}; data.questions.forEach(function (q, i) { idx[q.id] = i; });
    var deck = data.questions.filter(function (q) {
      if (only) return only.has(q.id);
      return kinds.indexOf(q.kind) >= 0 && units.indexOf(q.unit) >= 0;
    });
    deck.sort(function (a, b) { return (uo[a.unit] - uo[b.unit]) || (idx[a.id] - idx[b.id]); });
    return opt.shuffle ? shuffle(deck, opt.rng) : deck;
  }

  /** 유형 선택에 따른 단원별 문항 수 */
  function countUnits(data, kinds) {
    var c = {};
    data.units.forEach(function (u) { c[u.id] = 0; });
    data.questions.forEach(function (q) { if (kinds.indexOf(q.kind) >= 0) c[q.unit]++; });
    return c;
  }
  function countKinds(data) {
    var c = {};
    data.kinds.forEach(function (k) { c[k.id] = 0; });
    data.questions.forEach(function (q) { c[q.kind]++; });
    return c;
  }

  /* ---------- 북마크 ---------- */
  function makeStore(storage) {
    var mem = {};
    function get(k) { try { var v = storage.getItem(k); return v === null ? (mem[k] || null) : v; } catch (e) { return mem[k] || null; } }
    function set(k, v) { mem[k] = v; try { storage.setItem(k, v); } catch (e) { /* 저장 불가 환경: 메모리만 사용 */ } }
    function load() {
      try { var a = JSON.parse(get(BOOKMARK_KEY) || '[]'); return Array.isArray(a) ? a : []; } catch (e) { return []; }
    }
    function save(ids) { set(BOOKMARK_KEY, JSON.stringify(ids)); }
    return {
      list: load,
      has: function (id) { return load().indexOf(id) >= 0; },
      add: function (id) { var l = load(); if (l.indexOf(id) < 0) { l.push(id); save(l); return true; } return false; },
      remove: function (id) { var l = load(); var i = l.indexOf(id); if (i >= 0) { l.splice(i, 1); save(l); return true; } return false; },
      replace: function (ids) { save(Array.from(new Set(ids))); },
      clear: function () { save([]); },
      getPrefs: function () { try { return JSON.parse(get(PREF_KEY) || '{}') || {}; } catch (e) { return {}; } },
      setPrefs: function (p) { set(PREF_KEY, JSON.stringify(p)); }
    };
  }

  /** 북마크 ID를 데이터 순서로 정렬 (알 수 없는 ID는 뒤로) */
  function sortIds(ids, order) {
    return ids.slice().sort(function (a, b) {
      var ia = order.has(a) ? order.get(a) : 1e9, ib = order.has(b) ? order.get(b) : 1e9;
      return ia - ib || (a < b ? -1 : 1);
    });
  }

  function formatExport(ids, order, now) {
    var d = now || new Date();
    var pad = function (n) { return (n < 10 ? '0' : '') + n; };
    var stamp = d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes());
    var sorted = sortIds(ids, order);
    return ['# 면역학 개론 기출 퀴즈 북마크 v1', '# exported: ' + stamp, '# count: ' + sorted.length, ''].concat(sorted).join('\n') + '\n';
  }

  /** txt에서 문제 ID 추출. '#' 이후는 주석. 공백/쉼표/줄바꿈 구분 */
  function parseImport(text, validSet) {
    var ids = [], unknown = [], seen = new Set();
    String(text || '').replace(/^﻿/, '').split(/\r?\n/).forEach(function (line) {
      line = line.replace(/#.*/, '');
      line.split(/[\s,;]+/).forEach(function (tok) {
        tok = tok.trim();
        if (!tok || seen.has(tok)) return;
        seen.add(tok);
        (validSet.has(tok) ? ids : unknown).push(tok);
      });
    });
    return { ids: ids, unknown: unknown };
  }

  function mergeBookmarks(current, imported, mode) {
    if (mode === 'replace') return Array.from(new Set(imported));
    return Array.from(new Set(current.concat(imported)));
  }

  /** 풀이 결과 집계 */
  function summarize(deck, answers) {
    var s = { total: deck.length, correct: 0, wrong: 0, dk: 0, skipped: 0, wrongIds: [] };
    deck.forEach(function (q) {
      var a = answers[q.id];
      if (!a) s.skipped++;
      else if (a.dk) { s.dk++; s.wrongIds.push(q.id); }
      else if (a.correct) s.correct++;
      else { s.wrong++; s.wrongIds.push(q.id); }
    });
    return s;
  }

  return {
    CIRCLED: CIRCLED, label: label, BOOKMARK_KEY: BOOKMARK_KEY,
    isCorrect: isCorrect, norm: norm, splitItems: splitItems, gradeShort: gradeShort, answerText: answerText,
    shuffle: shuffle, isFixedOrder: isFixedOrder, shuffleOptions: shuffleOptions,
    buildDeck: buildDeck, countUnits: countUnits, countKinds: countKinds,
    makeStore: makeStore, sortIds: sortIds, formatExport: formatExport, parseImport: parseImport,
    mergeBookmarks: mergeBookmarks, summarize: summarize
  };
});
