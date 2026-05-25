/* ============================================================
   FUENCE PODCAST — SHARED NAV & FOOTER (nav.js)
   ============================================================
   HOW TO EDIT NAVIGATION:
   → Add a page: find "EDIT: NAV LINKS" — copy a <li>, paste, change text+href
   → Change logo text: edit SITE_NAME / SITE_TAGLINE below
   → Add footer column: find "EDIT: FOOTER COLUMNS"
   → Add social link: find "EDIT: SOCIAL LINKS"

   PATH RULE: All hrefs use root-relative paths starting with /
   Example: /about/index.html  NOT  ../about/index.html
   This works because the site is served from fuence.com root.
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  /* ============================================================
     EDIT: SITE IDENTITY
     ============================================================ */
  const SITE_NAME    = 'Fuence Podcast';
  const SITE_TAGLINE = 'For Peace, For Humanity';
  const CURRENT_YEAR = new Date().getFullYear();

  /* ============================================================
     EDIT: NAV LINKS
     To add a new page: copy one <li> block, paste after it,
     change the href and link text.
     ============================================================ */
  const navHTML = `
  <nav class="navbar" id="navbar">
    <div class="container">
      <div class="navbar-inner">

        <a href="/index.html" class="navbar-logo">
          <div class="logo-icon">F</div>
          <div>
            <span class="logo-text">${SITE_NAME}</span>
            <span class="logo-sub">${SITE_TAGLINE}</span>
          </div>
        </a>

        <!-- DESKTOP NAV — EDIT: ADD/REMOVE LINKS HERE -->
        <ul class="navbar-nav">
          <li><a href="/index.html">Home</a></li>
          <li><a href="/about/index.html">About</a></li>
          <li><a href="/series/index.html">Series</a></li>
          <li><a href="/publications/index.html">Publications</a></li>
          <li><a href="/community/index.html">Community</a></li>
          <li><a href="/contact/index.html">Contact</a></li>
          <!-- EDIT: Support CTA button — change link or text -->
          <li class="nav-cta"><a href="/support/index.html">☕ Support Us</a></li>
          <!-- ================================================
               TO ADD A NEW PAGE IN NAV:
               <li><a href="/YOURPAGE/index.html">Page Name</a></li>
               ================================================ -->
        </ul>

        <button class="navbar-toggle" id="navToggle" aria-label="Toggle menu">
          <span></span><span></span><span></span>
        </button>
      </div>

      <!-- MOBILE MENU — EDIT: MIRROR DESKTOP LINKS ABOVE -->
      <div class="navbar-menu" id="navMenu">
        <a href="/index.html">Home</a>
        <a href="/about/index.html">About</a>
        <a href="/series/index.html">Series</a>
        <a href="/publications/index.html">Publications</a>
        <a href="/community/index.html">Community</a>
        <a href="/contact/index.html">Contact</a>
        <div class="menu-cta"><a href="/support/index.html">☕ Support Us</a></div>
      </div>
    </div>
  </nav>`;

  /* ============================================================
     EDIT: FOOTER COLUMNS
     Column 1: Brand (auto). Columns 2-4: edit below.
     To add a new series to footer: add a new <li> under Series.
     ============================================================ */
  const footerHTML = `
  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">

        <!-- COLUMN 1: Brand — auto-generated -->
        <div class="footer-brand">
          <a href="/index.html" class="navbar-logo">
            <div class="logo-icon">F</div>
            <div>
              <span class="logo-text">${SITE_NAME}</span>
              <span class="logo-sub">${SITE_TAGLINE}</span>
            </div>
          </a>
          <!-- EDIT: Footer tagline -->
          <p class="footer-tagline">
            Independent research and analysis on global affairs,
            sovereignty, and the forces shaping humanity's future —
            presented as a podcast series.
          </p>
          <p class="footer-tagline-sub">Vision · Genesis · Legacy</p>
        </div>

        <!-- COLUMN 2: Series — EDIT: Add new series links here -->
        <div class="footer-col">
          <h4>Series</h4>
          <ul>
            <li><a href="/series/bangladesh/index.html">Bangladesh</a></li>
            <li><a href="/series/india/index.html">India & China</a></li>
            <li><a href="/series/index.html">Africa (Soon)</a></li>
            <li><a href="/series/index.html">Youth & Future (Soon)</a></li>
            <!-- ADD NEW SERIES: <li><a href="/series/TOPIC/index.html">Topic</a></li> -->
          </ul>
        </div>

        <!-- COLUMN 3: Research -->
        <div class="footer-col">
          <h4>Research</h4>
          <ul>
            <li><a href="/publications/index.html">All Publications</a></li>
            <li><a href="/publications/index.html#reports">Reports</a></li>
            <li><a href="/publications/index.html#op-eds">Op-Eds</a></li>
            <li><a href="/publications/index.html#briefs">Briefs</a></li>
            <li><a href="/community/index.html#forum">Forum</a></li>
          </ul>
        </div>

        <!-- COLUMN 4: Support & Legal -->
        <div class="footer-col">
          <h4>Support</h4>
          <ul>
            <!-- EDIT: Replace # with your platform links -->
            <li><a href="https://buymeacoffee.com/fuence" target="_blank">☕ Buy Me a Coffee</a></li>
            <li><a href="https://patreon.com/Fuence" target="_blank">🎙 Patreon</a></li>
            <li><a href="https://ko-fi.com/fuence" target="_blank">Ko-fi</a></li>
            <li><a href="/about/index.html#mission">Our Mission</a></li>
          </ul>
        </div>

      </div>

      <!-- FOOTER BOTTOM BAR -->
      <div class="footer-bottom">
        <p>&copy; ${CURRENT_YEAR} ${SITE_NAME}. All rights reserved.</p>

        <!-- EDIT: SOCIAL LINKS — replace # with real URLs -->
        <div style="display:flex;gap:16px;flex-wrap:wrap">
          <a href="https://x.com/Fuence4w" target="_blank">Twitter / X</a>
          <a href="https://www.youtube.com/@fuence" target="_blank">YouTube</a>
          <a href="https://substack.com/@fuence" target="_blank">Substack</a>
          <a href="https://discord.gg/NnhTegVXg" target="_blank">Discord</a>
        </div>

        <div class="footer-legal">
          <a href="/terms-of-use/index.html">Terms of Use</a>
          <a href="/privacy-policy/index.html">Privacy Policy</a>
          <a href="/contact/index.html">Contact</a>
        </div>
      </div>
    </div>
  </footer>`;

  /* ============================================================
     INJECT — do not edit below
     ============================================================ */
  const navEl = document.getElementById('nav-placeholder');
  if (navEl) navEl.outerHTML = navHTML;

  const footerEl = document.getElementById('footer-placeholder');
  if (footerEl) footerEl.innerHTML = footerHTML;

  // Scroll effect
  const navbar = document.getElementById('navbar');
  if (navbar) window.addEventListener('scroll', () => navbar.classList.toggle('scrolled', scrollY > 20));

  // Mobile toggle
  const toggle = document.getElementById('navToggle');
  const menu   = document.getElementById('navMenu');
  if (toggle && menu) toggle.addEventListener('click', () => menu.classList.toggle('open'));

  // Active link highlight
  const path = window.location.pathname;
  document.querySelectorAll('.navbar-nav a, .navbar-menu a').forEach(a => {
    const href = a.getAttribute('href') || '';
    if (href === '/index.html' && (path === '/' || path.endsWith('/index.html') && path.split('/').length <= 2)) {
      a.classList.add('active');
    } else if (href !== '/index.html' && href !== '#' && path.includes(href.replace('/index.html', ''))) {
      a.classList.add('active');
    }
  });
});
