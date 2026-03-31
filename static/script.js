/* ── Timer ─────────────────────────────────────────────────────────────── */

function initTimer(totalSecs) {
  const el    = document.getElementById('timer-display');
  const form  = document.getElementById('quiz-form');
  if (!el) return;

  let remaining = totalSecs;

  function fmt(s) {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${sec.toString().padStart(2, '0')}`;
  }

  function tick() {
    el.textContent = fmt(remaining);
    const timerEl = el.closest('.timer');

    if (remaining <= 0) {
      timerEl.classList.add('urgent');
      el.textContent = '0:00';
      if (form) form.submit();
      return;
    }

    if (remaining <= 30) {
      timerEl.classList.remove('warn');
      timerEl.classList.add('urgent');
    } else if (remaining <= 60) {
      timerEl.classList.add('warn');
    }

    remaining--;
    setTimeout(tick, 1000);
  }

  tick();
}

/* ── Progress bar ──────────────────────────────────────────────────────── */

function initProgress(total) {
  const answered = {};
  const radios   = document.querySelectorAll('input[type="radio"]');
  const fill     = document.getElementById('progress-fill');
  const label    = document.getElementById('progress-label');
  if (!fill) return;

  function update() {
    const count = Object.keys(answered).length;
    const pct   = total > 0 ? Math.round(count / total * 100) : 0;
    fill.style.width = pct + '%';
    if (label) label.textContent = `${count} / ${total} answered`;
  }

  radios.forEach(r => {
    r.addEventListener('change', () => {
      answered[r.name] = true;
      update();
    });
  });

  update();
}

/* ── Keyboard shortcuts (A/B/C/D to pick option for current visible Q) ─── */

function initKeyNav() {
  const keys = { a: 0, b: 1, c: 2, d: 3 };
  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    const idx = keys[e.key.toLowerCase()];
    if (idx === undefined) return;

    // Find visible / first unanswered question block
    const blocks = document.querySelectorAll('.question-block');
    for (const block of blocks) {
      const radios = block.querySelectorAll('input[type="radio"]');
      const answered = Array.from(radios).some(r => r.checked);
      if (!answered) {
        if (radios[idx]) {
          radios[idx].checked = true;
          radios[idx].dispatchEvent(new Event('change', { bubbles: true }));
          // Scroll the next block into view
          const next = block.nextElementSibling;
          if (next) next.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        break;
      }
    }
  });
}

/* ── Submit guard ──────────────────────────────────────────────────────── */

function initSubmitGuard(total) {
  const form = document.getElementById('quiz-form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    const answered = new Set(
      Array.from(form.querySelectorAll('input[type="radio"]:checked'))
           .map(r => r.name)
    ).size;

    if (answered < total) {
      const ok = confirm(`You've answered ${answered} of ${total} questions. Submit anyway?`);
      if (!ok) e.preventDefault();
    }
  });
}

/* ── Category / difficulty picker (index page) ─────────────────────────── */

function initPicker(groupClass, inputId) {
  const btns  = document.querySelectorAll('.' + groupClass);
  const input = document.getElementById(inputId);
  if (!btns.length || !input) return;

  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      btns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      input.value = btn.dataset.value;
    });
  });
}

/* ── Leaderboard live filter ───────────────────────────────────────────── */

function initLeaderboardFilter() {
  const catSel  = document.getElementById('lb-cat');
  const diffSel = document.getElementById('lb-diff');
  if (!catSel) return;

  function reload() {
    const params = new URLSearchParams({
      category:   catSel.value,
      difficulty: diffSel.value,
    });
    window.location.search = params.toString();
  }

  catSel.addEventListener('change', reload);
  diffSel.addEventListener('change', reload);
}

/* ── Init ──────────────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
  const timerEl = document.getElementById('timer-display');
  if (timerEl) {
    const secs = parseInt(timerEl.dataset.total, 10);
    if (!isNaN(secs)) initTimer(secs);
  }

  const totalQ = parseInt(document.body.dataset.totalQuestions, 10);
  if (!isNaN(totalQ)) {
    initProgress(totalQ);
    initSubmitGuard(totalQ);
    initKeyNav();
  }

  initPicker('cat-btn', 'sel-category');
  initPicker('diff-btn', 'sel-difficulty');
  initLeaderboardFilter();
});