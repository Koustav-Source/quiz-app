/* ═══════════════════════════════════════════════════════════
   THEME TOGGLE
═══════════════════════════════════════════════════════════ */

function initTheme() {
  const STORAGE_KEY = 'quizos-theme';
  const root        = document.documentElement;
  const toggleBtn   = document.getElementById('theme-toggle');

  // Icons for the thumb
  const ICON_DARK  = '🌙';
  const ICON_LIGHT = '☀';

  function getThumb() {
    return toggleBtn ? toggleBtn.querySelector('.theme-toggle-thumb') : null;
  }

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
    const thumb = getThumb();
    if (thumb) {
      thumb.textContent = theme === 'light' ? ICON_LIGHT : ICON_DARK;
    }
    if (toggleBtn) {
      toggleBtn.setAttribute('aria-label',
        theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'
      );
    }
  }

  // Restore saved preference, or honour OS preference
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) {
    applyTheme(saved);
  } else {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    applyTheme(prefersDark ? 'dark' : 'light');
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const current = root.getAttribute('data-theme') || 'dark';
      applyTheme(current === 'dark' ? 'light' : 'dark');
    });
  }
}

/* ═══════════════════════════════════════════════════════════
   TIMER
═══════════════════════════════════════════════════════════ */

function initTimer(totalSecs) {
  const el   = document.getElementById('timer-display');
  const form = document.getElementById('quiz-form');
  if (!el) return;

  let remaining = totalSecs;

  function fmt(s) {
    const m   = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${sec.toString().padStart(2, '0')}`;
  }

  function tick() {
    el.textContent = fmt(remaining);
    const timerEl  = el.closest('.timer');

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

/* ═══════════════════════════════════════════════════════════
   PROGRESS BAR
═══════════════════════════════════════════════════════════ */

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
    if (label) {
      const span = label.querySelector('.progress-answered');
      if (span) span.textContent = count;
    }
  }

  radios.forEach(r => {
    r.addEventListener('change', () => {
      answered[r.name] = true;
      update();
    });
  });

  update();
}

/* ═══════════════════════════════════════════════════════════
   KEYBOARD SHORTCUTS — A/B/C/D
═══════════════════════════════════════════════════════════ */

function initKeyNav() {
  const keys = { a: 0, b: 1, c: 2, d: 3 };

  document.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    const idx = keys[e.key.toLowerCase()];
    if (idx === undefined) return;

    const blocks = document.querySelectorAll('.question-block');
    for (const block of blocks) {
      const radios   = block.querySelectorAll('input[type="radio"]');
      const isAnswered = Array.from(radios).some(r => r.checked);
      if (!isAnswered) {
        if (radios[idx]) {
          radios[idx].checked = true;
          radios[idx].dispatchEvent(new Event('change', { bubbles: true }));
          const next = block.nextElementSibling;
          if (next && next.classList.contains('question-block')) {
            next.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }
        break;
      }
    }
  });
}

/* ═══════════════════════════════════════════════════════════
   SUBMIT GUARD
═══════════════════════════════════════════════════════════ */

function initSubmitGuard(total) {
  const form = document.getElementById('quiz-form');
  if (!form) return;

  form.addEventListener('submit', (e) => {
    const answered = new Set(
      Array.from(form.querySelectorAll('input[type="radio"]:checked'))
           .map(r => r.name)
    ).size;

    if (answered < total) {
      const ok = confirm(
        `You've answered ${answered} of ${total} questions.\nSubmit anyway?`
      );
      if (!ok) e.preventDefault();
    }
  });
}

/* ═══════════════════════════════════════════════════════════
   CATEGORY / DIFFICULTY PICKER
═══════════════════════════════════════════════════════════ */

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

/* ═══════════════════════════════════════════════════════════
   LEADERBOARD LIVE FILTER
═══════════════════════════════════════════════════════════ */

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

/* ═══════════════════════════════════════════════════════════
   INIT
═══════════════════════════════════════════════════════════ */

// Theme runs ASAP (not DOMContentLoaded) to avoid flash of wrong theme
initTheme();

document.addEventListener('DOMContentLoaded', () => {
  // Timer
  const timerEl = document.getElementById('timer-display');
  if (timerEl) {
    const secs = parseInt(timerEl.dataset.total, 10);
    if (!isNaN(secs)) initTimer(secs);
  }

  // Quiz-page features
  const totalQ = parseInt(document.body.dataset.totalQuestions, 10);
  if (!isNaN(totalQ)) {
    initProgress(totalQ);
    initSubmitGuard(totalQ);
    initKeyNav();
  }

  // Config pickers
  initPicker('cat-btn',  'sel-category');
  initPicker('diff-btn', 'sel-difficulty');

  // Leaderboard
  initLeaderboardFilter();
});