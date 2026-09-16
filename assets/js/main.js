/* ==========================================================================
   Santa's Legacy - site behaviour
   No framework, no build step. Everything degrades: with JS off you still
   get the whole page, a <noscript> link to the trailer file, and every
   screenshot at thumbnail size.
   ========================================================================== */
(function () {
  'use strict';

  /* ======================================================================
     CONFIG - the only block you need to edit
     ====================================================================== */
  var CONFIG = {
    // Google Analytics 4 measurement ID. Create a property at
    // analytics.google.com -> Admin -> Data streams -> Web, copy the
    // "G-" ID and paste it here. Until it is set, nothing is loaded.
    GA_MEASUREMENT_ID: 'G-NNKBKQVN5S',

    // Show the consent banner before loading Analytics. Required in the
    // EU/UK. Set to false only if you have a different consent tool.
    REQUIRE_CONSENT: true,

    // localStorage key holding the visitor's choice.
    CONSENT_KEY: 'sl_consent_v1'
  };

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ======================================================================
     Google Analytics 4, behind consent
     ====================================================================== */
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;

  var analyticsLoaded = false;

  function idLooksReal() {
    return /^G-[A-Z0-9]{6,}$/.test(CONFIG.GA_MEASUREMENT_ID) &&
           CONFIG.GA_MEASUREMENT_ID !== 'G-XXXXXXXXXX';
  }

  function loadAnalytics() {
    if (analyticsLoaded || !idLooksReal()) return;
    analyticsLoaded = true;

    // Consent Mode v2 defaults, set before the tag runs.
    gtag('consent', 'default', {
      ad_storage: 'denied',
      ad_user_data: 'denied',
      ad_personalization: 'denied',
      analytics_storage: 'granted',
      functionality_storage: 'granted',
      security_storage: 'granted'
    });

    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + CONFIG.GA_MEASUREMENT_ID;
    document.head.appendChild(s);

    gtag('js', new Date());
    gtag('config', CONFIG.GA_MEASUREMENT_ID, { anonymize_ip: true });
  }

  /** Send an event if - and only if - analytics is actually running. */
  function track(name, params) {
    if (analyticsLoaded) gtag('event', name, params || {});
  }

  function readConsent() {
    try { return localStorage.getItem(CONFIG.CONSENT_KEY); } catch (e) { return null; }
  }
  function writeConsent(v) {
    try { localStorage.setItem(CONFIG.CONSENT_KEY, v); } catch (e) { /* private mode */ }
  }

  function initConsent() {
    var banner = $('#consent');
    if (!idLooksReal()) return;                 // nothing to consent to yet

    if (!CONFIG.REQUIRE_CONSENT) { loadAnalytics(); return; }

    var choice = readConsent();
    if (choice === 'granted') { loadAnalytics(); return; }
    if (choice === 'denied') return;

    if (!banner) { return; }
    // Delay a beat so it does not fight the hero for attention.
    setTimeout(function () { banner.classList.add('is-open'); }, 900);

    $('#consentYes').addEventListener('click', function () {
      writeConsent('granted');
      banner.classList.remove('is-open');
      loadAnalytics();
      track('consent_granted');
    });
    $('#consentNo').addEventListener('click', function () {
      writeConsent('denied');
      banner.classList.remove('is-open');
    });
  }

  /** The "change my choice" control on the privacy page. */
  function initConsentControls() {
    var btn = $('#consentReset');
    var state = $('#consentState');
    if (!btn && !state) return;

    var choice = readConsent();
    if (state) {
      state.textContent = !idLooksReal()
        ? 'Analytics is not configured on this site yet, so nothing is being collected.'
        : choice === 'granted' ? 'Currently: analytics accepted.'
        : choice === 'denied'  ? 'Currently: analytics declined.'
        : 'You have not chosen yet.';
    }
    if (btn) {
      btn.addEventListener('click', function () {
        try { localStorage.removeItem(CONFIG.CONSENT_KEY); } catch (e) { /* private mode */ }
        // Drop the GA cookies this site set, so declining really clears them.
        document.cookie.split(';').forEach(function (c) {
          var name = c.split('=')[0].trim();
          if (name.indexOf('_ga') === 0) {
            document.cookie = name + '=; Max-Age=0; path=/';
            document.cookie = name + '=; Max-Age=0; path=/; domain=.' + location.hostname;
          }
        });
        location.reload();
      });
    }
  }

  /* ======================================================================
     Header: mobile nav + stuck state
     ====================================================================== */
  function initHeader() {
    var header = $('#siteHeader');
    var toggle = $('#navToggle');
    var nav = $('#primaryNav');

    if (toggle && nav) {
      toggle.addEventListener('click', function () {
        var open = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', String(!open));
        nav.classList.toggle('is-open', !open);
      });
      nav.addEventListener('click', function (e) {
        if (e.target.tagName === 'A') {
          toggle.setAttribute('aria-expanded', 'false');
          nav.classList.remove('is-open');
        }
      });
    }

    if (header) {
      var onScroll = function () {
        header.classList.toggle('is-stuck', window.scrollY > 24);
      };
      onScroll();
      window.addEventListener('scroll', onScroll, { passive: true });
    }
  }

  /* ======================================================================
     Trailer: nothing is fetched until the poster is clicked
     ====================================================================== */
  function initPlayer() {
    var video = $('#trailerVideo');
    var btn = $('#playerBtn');
    if (!video || !btn) return;

    btn.addEventListener('click', function () {
      btn.style.display = 'none';
      // Controls are added only now - before this the poster overlay is the
      // whole interface, and a native control bar would show through it.
      video.setAttribute('controls', '');
      video.play().catch(function () { /* the controls are there either way */ });
      track('trailer_play', { video_title: "Santa's Legacy announcement trailer" });
    });
    // The overlay does not come back when the video ends: the native
    // controls are the replay button from that point on, and the two
    // stacked on each other read as two different play affordances.
  }

  /* ======================================================================
     Screenshot lightbox
     ====================================================================== */
  function initLightbox() {
    var box = $('#lightbox');
    var img = $('#lightboxImg');
    var cap = $('#lightboxCap');
    var shots = $$('#gallery .shot');
    if (!box || !shots.length) return;

    var index = 0;
    var lastFocus = null;

    function show(i) {
      index = (i + shots.length) % shots.length;
      var el = shots[index];
      img.src = el.getAttribute('data-full');
      img.alt = el.querySelector('img') ? el.querySelector('img').alt : '';
      cap.textContent = el.getAttribute('data-cap') || '';
    }
    function open(i) {
      lastFocus = document.activeElement;
      show(i);
      box.classList.add('is-open');
      document.body.style.overflow = 'hidden';
      $('#lightboxClose').focus();
      track('screenshot_open', { screenshot: shots[index].getAttribute('data-full') });
    }
    function close() {
      box.classList.remove('is-open');
      document.body.style.overflow = '';
      img.src = '';
      if (lastFocus) lastFocus.focus();
    }

    shots.forEach(function (el, i) {
      el.addEventListener('click', function () { open(i); });
    });
    $('#lightboxClose').addEventListener('click', close);
    $('#lightboxPrev').addEventListener('click', function () { show(index - 1); });
    $('#lightboxNext').addEventListener('click', function () { show(index + 1); });
    box.addEventListener('click', function (e) {
      if (e.target === box || e.target === img) close();
    });
    document.addEventListener('keydown', function (e) {
      if (!box.classList.contains('is-open')) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowLeft') show(index - 1);
      else if (e.key === 'ArrowRight') show(index + 1);
    });
  }

  /* ======================================================================
     Scroll reveal
     ====================================================================== */
  function initReveal() {
    var items = $$('.reveal');
    if (!items.length) return;
    if (reduceMotion || !('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });
  }

  /* ======================================================================
     Hero snowfall - decorative, skipped entirely under reduced motion
     ====================================================================== */
  function initSnow() {
    var canvas = $('#snowCanvas');
    if (!canvas || reduceMotion) return;

    var ctx = canvas.getContext('2d');
    var flakes = [];
    var running = true;
    var w = 0, h = 0, dpr = Math.min(window.devicePixelRatio || 1, 2);

    function resize() {
      var rect = canvas.getBoundingClientRect();
      w = rect.width; h = rect.height;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var count = Math.min(120, Math.round(w * h / 12000));
      flakes = [];
      for (var i = 0; i < count; i++) {
        flakes.push({
          x: Math.random() * w,
          y: Math.random() * h,
          r: 0.9 + Math.random() * 2.2,
          vy: 14 + Math.random() * 34,
          drift: (Math.random() - 0.5) * 22,
          phase: Math.random() * Math.PI * 2,
          a: 0.25 + Math.random() * 0.5
        });
      }
    }

    var last = 0;
    function frame(t) {
      if (!running) return;
      var dt = last ? Math.min((t - last) / 1000, 0.05) : 0.016;
      last = t;
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = '#ffffff';
      for (var i = 0; i < flakes.length; i++) {
        var f = flakes[i];
        f.y += f.vy * dt;
        f.phase += dt;
        f.x += Math.sin(f.phase) * f.drift * dt;
        if (f.y - f.r > h) { f.y = -f.r; f.x = Math.random() * w; }
        if (f.x < -10) f.x = w + 10; else if (f.x > w + 10) f.x = -10;
        ctx.globalAlpha = f.a;
        ctx.beginPath();
        ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;
      requestAnimationFrame(frame);
    }

    function start() { if (!running) { running = true; last = 0; requestAnimationFrame(frame); } }
    function stop() { running = false; }

    resize();
    requestAnimationFrame(frame);

    var rt;
    window.addEventListener('resize', function () {
      clearTimeout(rt);
      rt = setTimeout(resize, 200);
    }, { passive: true });

    document.addEventListener('visibilitychange', function () {
      document.hidden ? stop() : start();
    });

    // Stop burning frames once the hero has scrolled away.
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (e) {
        e[0].isIntersecting ? start() : stop();
      }, { threshold: 0 }).observe(canvas);
    }
  }

  /* ======================================================================
     Outbound / CTA tracking
     ====================================================================== */
  function initTracking() {
    $$('[data-cta]').forEach(function (el) {
      el.addEventListener('click', function () {
        track('wishlist_click', {
          link_location: el.getAttribute('data-cta'),
          link_url: el.getAttribute('href')
        });
      });
    });

    $$('a[href^="mailto:"]').forEach(function (el) {
      el.addEventListener('click', function () { track('email_click'); });
    });

    $$('.dl[download], a[download]').forEach(function (el) {
      el.addEventListener('click', function () {
        track('file_download', { file_name: el.getAttribute('href') });
      });
    });
  }

  /* ======================================================================
     Small things
     ====================================================================== */
  function initMisc() {
    var y = $('#year');
    if (y) y.textContent = String(new Date().getFullYear());
  }

  /* ====================================================================== */
  function boot() {
    initHeader();
    initPlayer();
    initLightbox();
    initReveal();
    initSnow();
    initTracking();
    initMisc();
    initConsent();
    initConsentControls();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
