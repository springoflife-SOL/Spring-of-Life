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

  document.addEventListener('DOMContentLoaded', function () {
    initReveal();
    initMobileNav();
    initHeaderState();
  });
})();
