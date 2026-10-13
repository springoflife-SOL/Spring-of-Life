/* Spring of Life — shared interactions. 의존성 없음. */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* --- Reveal on scroll --- */
  function initReveal() {
    var items = document.querySelectorAll('.reveal');
    if (!items.length) return;

    if (reduceMotion || !('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-visible'); });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.1 });

    items.forEach(function (el) { observer.observe(el); });
  }

  /* --- Mobile navigation --- */
  function initMobileNav() {
    var btn = document.getElementById('menuBtn');
    var nav = document.getElementById('mobileNav');
    if (!btn || !nav) return;

    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!open));
      btn.setAttribute('aria-label', open ? 'Open menu' : 'Close menu');
      nav.hidden = open;
    });

    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape' || nav.hidden) return;
      btn.setAttribute('aria-expanded', 'false');
      btn.setAttribute('aria-label', 'Open menu');
      nav.hidden = true;
      btn.focus();
    });
  }

  /* --- Nav dropdown (Programs / We In Campus) --- */
  function initDropdownNav() {
    var items = document.querySelectorAll('.nav__item--dropdown');
    if (!items.length) return;

    items.forEach(function (item) {
      var btn = item.querySelector('.nav__link--dropdown');
      if (!btn) return;

      function open() {
        item.setAttribute('data-open', 'true');
        btn.setAttribute('aria-expanded', 'true');
      }
      function close() {
        item.removeAttribute('data-open');
        btn.setAttribute('aria-expanded', 'false');
      }

      btn.addEventListener('click', function () {
        if (item.getAttribute('data-open') === 'true') close(); else open();
      });
      item.addEventListener('mouseenter', open);
      item.addEventListener('mouseleave', close);
      document.addEventListener('click', function (e) {
        if (!item.contains(e.target)) close();
      });
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') { close(); btn.focus(); }
      });
    });
  }

  /* --- Header scroll state --- */
  function initHeaderState() {
    var header = document.getElementById('header');
    if (!header) return;
    var ticking = false;

    function update() {
      header.classList.toggle('header--scrolled', window.scrollY > 8);
      ticking = false;
    }

    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }, { passive: true });

    update();
  }

  /* --- Poster lightbox --- */
  function initLightbox() {
    var box = document.getElementById('lightbox');
    var img = document.getElementById('lightboxImg');
    var cap = document.getElementById('lightboxCap');
    var closeBtn = document.getElementById('lightboxClose');
    var triggers = document.querySelectorAll('.poster');
    if (!box || !img || !cap || !closeBtn || !triggers.length) return;

    var lastFocused = null;

    function open(trigger) {
      lastFocused = trigger;
      img.src = trigger.getAttribute('data-full');
      img.alt = trigger.getAttribute('data-caption') || '';
      cap.textContent = trigger.getAttribute('data-caption') || '';
      box.hidden = false;
      document.body.classList.add('is-locked');
      closeBtn.focus();
    }

    function close() {
      box.hidden = true;
      img.src = '';
      document.body.classList.remove('is-locked');
      if (lastFocused) lastFocused.focus();
    }

    triggers.forEach(function (trigger) {
      trigger.addEventListener('click', function () { open(trigger); });
    });

    closeBtn.addEventListener('click', close);

    box.addEventListener('click', function (e) {
      if (e.target === box) close();
    });

    document.addEventListener('keydown', function (e) {
      if (box.hidden) return;
      if (e.key === 'Escape') { close(); return; }
      if (e.key === 'Tab') { e.preventDefault(); closeBtn.focus(); }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initReveal();
    initMobileNav();
    initDropdownNav();
    initHeaderState();
    initLightbox();
  });
})();
