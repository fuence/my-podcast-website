/* ============================================================
   FUENCE PODCAST — MAIN JS (main.js)
   Handles: scroll reveal, tab switching, smooth scroll
   You do NOT need to edit this file.
   ============================================================ */
document.addEventListener('DOMContentLoaded', function () {

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', function(e) {
      const t = document.querySelector(this.getAttribute('href'));
      if (t) { e.preventDefault(); t.scrollIntoView({behavior:'smooth',block:'start'}); }
    });
  });

  // Scroll reveal
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); observer.unobserve(e.target); }});
  }, {threshold:.1});
  document.querySelectorAll('.scroll-reveal').forEach(el => observer.observe(el));

  // Tab switching — used on publications page
  // Buttons: data-tab-target="id" inside parent data-tab-group
  // Panes:   data-tab-content="id"
  document.querySelectorAll('[data-tab-group]').forEach(group => {
    const btns  = group.querySelectorAll('[data-tab-target]');
    const panes = document.querySelectorAll('[data-tab-content]');
    function activate(targetId) {
      btns.forEach(b  => b.classList.toggle('tab-active', b.dataset.tabTarget === targetId));
      panes.forEach(p => p.style.display = p.dataset.tabContent === targetId ? 'block' : 'none');
    }
    btns.forEach(b => b.addEventListener('click', () => activate(b.dataset.tabTarget)));
    if (btns[0]) activate(btns[0].dataset.tabTarget); // activate first tab
  });

});
