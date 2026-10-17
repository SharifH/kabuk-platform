/* KabuK Platform — site behaviour (vanilla JS, no dependencies).
   Progressive enhancement: every page is fully readable without this file. */
(function () {
  'use strict';
  var doc = document, root = doc.documentElement;
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function storeLocale(code) { try { localStorage.setItem('kbk-locale', code); } catch (e) { /* storage unavailable */ } }

  /* ---- Config-driven links (site-config.json) ---------------------------- */
  // Resolve the site root from <html data-root> so the site works at a domain root
  // or under a subpath (e.g. GitHub Pages /kabuk-platform/).
  var siteRoot = new URL(root.getAttribute('data-root') || './', location.href);
  var configPromise = fetch(new URL('site-config.json', siteRoot).href, { cache: 'no-cache' })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .catch(function (e) { console.warn('[kabuk] site-config.json unavailable', e); return null; });

  configPromise.then(function (c) {
    if (!c || !c.urls) return;
    doc.querySelectorAll('[data-config-link]').forEach(function (a) {
      var u = c.urls[a.getAttribute('data-config-link')];
      if (u) a.href = u;
    });
  });

  /* ---- Navigation: disclosure menus + mobile panel ----------------------- */
  var triggers = Array.prototype.slice.call(doc.querySelectorAll('.nav-trigger'));
  function closeAll(except) {
    triggers.forEach(function (b) { if (b !== except) b.setAttribute('aria-expanded', 'false'); });
  }
  triggers.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = btn.getAttribute('aria-expanded') === 'true';
      closeAll(btn);
      btn.setAttribute('aria-expanded', open ? 'false' : 'true');
      if (!open) {
        var first = doc.getElementById(btn.getAttribute('aria-controls'));
        first = first && first.querySelector('a');
        if (first && e.detail === 0) first.focus(); // keyboard activation moves focus into the menu
      }
    });
  });
  doc.addEventListener('click', function (e) {
    if (!e.target.closest('.nav-item')) closeAll();
  });
  doc.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var openBtn = triggers.filter(function (b) { return b.getAttribute('aria-expanded') === 'true'; })[0];
    if (openBtn) { closeAll(); openBtn.focus(); return; }
    if (navToggle && navToggle.getAttribute('aria-expanded') === 'true') { setMobile(false); navToggle.focus(); }
  });
  // Close a desktop menu when focus leaves it
  doc.querySelectorAll('.nav-item').forEach(function (item) {
    item.addEventListener('focusout', function (e) {
      if (!item.contains(e.relatedTarget) && window.innerWidth > 1080) {
        var b = item.querySelector('.nav-trigger'); if (b) b.setAttribute('aria-expanded', 'false');
      }
    });
  });

  var navToggle = doc.querySelector('.nav-toggle');
  var nav = doc.getElementById('site-nav');
  function setMobile(open) {
    navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    nav.classList.toggle('is-open', open);
    if (!open) closeAll();
  }
  if (navToggle && nav) {
    navToggle.addEventListener('click', function () { setMobile(navToggle.getAttribute('aria-expanded') !== 'true'); });
    nav.addEventListener('click', function (e) {
      var a = e.target.closest('a');
      if (a && a.hash && a.pathname === location.pathname) setMobile(false);
    });
  }

  /* ---- Language: remember explicit choices ------------------------------- */
  doc.querySelectorAll('[data-set-locale]').forEach(function (a) {
    a.addEventListener('click', function () { storeLocale(a.getAttribute('data-set-locale')); });
  });

  /* ---- Reveal on scroll -------------------------------------------------- */
  var revealables = doc.querySelectorAll('[data-reveal]');
  if (reduceMotion || !('IntersectionObserver' in window)) {
    revealables.forEach(function (el) { el.classList.add('is-visible'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('is-visible'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revealables.forEach(function (el) { io.observe(el); });
  }

  /* ---- Diagram: cycle a lit node so the architecture reads as coordinated  */
  if (!reduceMotion) {
    doc.querySelectorAll('.arch-grid').forEach(function (grid) {
      var nodes = grid.querySelectorAll('.arch-node'), i = 0, timer = null;
      function step() { nodes.forEach(function (n) { n.classList.remove('is-lit'); }); nodes[i % nodes.length].classList.add('is-lit'); i++; }
      var vis = new IntersectionObserver(function (en) {
        if (en[0].isIntersecting && !timer) { step(); timer = setInterval(step, 800); }
        else if (!en[0].isIntersecting && timer) { clearInterval(timer); timer = null; }
      });
      vis.observe(grid);
    });
  }

  /* ---- Integrations directory filter (Solutions #connect) ---------------- */
  Array.prototype.forEach.call(doc.querySelectorAll('[data-dir]'), function (dir) {
    var q = dir.querySelector('[data-dir-q]'), st = dir.querySelector('[data-dir-status]'), ty = dir.querySelector('[data-dir-type]');
    var items = dir.querySelectorAll('[data-dir-list] > li'), count = dir.querySelector('[data-dir-count]');
    var empty = dir.querySelector('[data-dir-empty]'), tpl = dir.getAttribute('data-count-template') || '{shown} / {total}';
    function apply() {
      var term = (q.value || '').trim().toLowerCase(), s = st.value, t = ty.value, shown = 0;
      Array.prototype.forEach.call(items, function (li) {
        var ok = (!term || li.getAttribute('data-name').indexOf(term) !== -1) &&
                 (!s || li.getAttribute('data-status') === s) && (!t || li.getAttribute('data-type') === t);
        li.hidden = !ok; if (ok) shown++;
      });
      count.textContent = tpl.replace('{shown}', shown).replace('{total}', items.length);
      empty.hidden = shown !== 0;
    }
    dir.querySelector('[data-dir-filters]').addEventListener('submit', function (e) { e.preventDefault(); });
    [q, st, ty].forEach(function (el) { el.addEventListener('input', apply); el.addEventListener('change', apply); });
  });

  /* ---- Contact form (mailto) --------------------------------------------- */
  var form = doc.getElementById('lead-form');
  if (!form) return;
  var ui = {};
  try { ui = JSON.parse(doc.getElementById('form-i18n').textContent); } catch (e) { console.warn('[kabuk] form strings missing', e); }
  var statusEl = doc.getElementById('form-status');
  var summary = doc.getElementById('form-summary');

  // Pre-select from query string: /contact/?type=hotel&interest=pricing
  var params = new URLSearchParams(location.search);
  [['type', 'orgType'], ['interest', 'interest']].forEach(function (p) {
    var v = params.get(p[0]), el = form.elements[p[1]];
    if (v && el && el.querySelector('option[value="' + CSS.escape(v) + '"]')) el.value = v;
  });

  var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  function fieldOf(el) { return el.closest('.field'); }
  function setError(el, msg) {
    var f = fieldOf(el), err = f && f.querySelector('.field-error');
    if (!f) return;
    f.classList.toggle('has-error', !!msg);
    if (msg) el.setAttribute('aria-invalid', 'true'); else el.removeAttribute('aria-invalid');
    if (err) err.textContent = msg || '';
  }
  function validate(el) {
    var e = ui.errors || {}, v = (el.type === 'checkbox') ? el.checked : el.value.trim(), msg = '';
    if (el.required && !v) msg = el.type === 'checkbox' ? e.privacy : (el.tagName === 'SELECT' ? e.select : e.required);
    else if (el.type === 'email' && v && !emailRe.test(v)) msg = e.email;
    setError(el, msg);
    return !msg;
  }
  Array.prototype.forEach.call(form.elements, function (el) {
    if (!el.name) return;
    el.addEventListener(el.tagName === 'SELECT' || el.type === 'checkbox' ? 'change' : 'blur', function () {
      if (fieldOf(el) && (fieldOf(el).classList.contains('has-error') || el.value)) validate(el);
    });
    // Clear an error as soon as it is fixed while typing, so the layout doesn't shift
    // under the pointer when the user then clicks the submit button.
    if (el.tagName !== 'SELECT' && el.type !== 'checkbox') {
      el.addEventListener('input', function () {
        if (fieldOf(el) && fieldOf(el).classList.contains('has-error')) validate(el);
      });
    }
  });

  function optionText(name) {
    var el = form.elements[name];
    if (!el || !el.value) return '';
    return el.tagName === 'SELECT' ? el.options[el.selectedIndex].text + ' [' + el.value + ']' : el.value.trim();
  }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    statusEl.innerHTML = '';
    var invalid = [];
    Array.prototype.forEach.call(form.elements, function (el) { if (el.name && !validate(el)) invalid.push(el); });
    if (invalid.length) {
      summary.textContent = (ui.errors && ui.errors.summary) || '';
      summary.hidden = false;
      invalid[0].focus();
      return;
    }
    summary.hidden = true;

    configPromise.then(function (c) {
      var leads = c && c.leads;
      var routeKey = leads && leads.organizationTypeRoute ? leads.organizationTypeRoute[form.elements.orgType.value] : null;
      var to = leads && leads.routes ? (leads.routes[routeKey] || leads.routes.general) : null;
      if (!to || !leads || leads.formMode !== 'mailto') {
        statusEl.innerHTML = '<p class="notice">' + escapeHtml(ui.configError || 'Not configured') + '</p>';
        return;
      }
      var L = ui.emailLabels || {};
      var lines = ['name', 'company', 'email', 'orgType', 'region', 'interest', 'systems'].map(function (k) {
        return (L[k] || k) + ': ' + optionText(k);
      });
      lines.push('', (L.message || 'Message') + ':', form.elements.message.value.trim());
      lines.push('', '—', 'Page: ' + location.href, 'Language: ' + root.getAttribute('data-locale'));
      var subject = (ui.emailSubject || '{prefix}: {company}')
        .replace('{prefix}', leads.subjectPrefix || 'KabuK Platform inquiry')
        .replace('{company}', form.elements.company.value.trim());
      var mailto = 'mailto:' + encodeURIComponent(to).replace('%40', '@') +
        '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(lines.join('\n'));

      statusEl.innerHTML = '<div class="notice notice-info"><span><strong>' + escapeHtml(ui.confirmation || '') + '</strong><br>' +
        escapeHtml(ui.fallback || '').replace('{email}', '<a href="mailto:' + escapeHtml(to) + '" dir="ltr">' + escapeHtml(to) + '</a>') + '</span></div>';
      window.location.href = mailto;
    });
  });

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (ch) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[ch]; });
  }
})();
