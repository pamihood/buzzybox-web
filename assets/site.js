// The film that opens the homepage. It plays muted as soon as it can - never
// for reduced motion or data saver, and never while it is off screen - with a
// pause and a sound button. Every failure lands on the poster: an autoplay the
// browser refuses shows a play button instead.
const film = document.querySelector('.film');
if (film) {
  const video = film.querySelector('video');
  const start = film.querySelector('.film-start');
  const pause = film.querySelector('.film-pause');
  const sound = film.querySelector('.film-sound');
  // What the visitor wants, kept apart from what the video is doing: scrolling
  // away pauses the film, but must not turn into "paused" when they come back.
  // Data saver counts as asking: the poster and a play button, no download.
  let wantsPlay = !window.matchMedia('(prefers-reduced-motion: reduce)').matches
    && !(navigator.connection && navigator.connection.saveData);
  let onScreen = true;
  let started = false;

  const render = () => {
    film.classList.toggle('is-paused', !wantsPlay);
    film.classList.toggle('has-sound', !video.muted);
    pause.setAttribute('aria-label', wantsPlay ? 'Pause the film' : 'Play the film');
    sound.setAttribute('aria-pressed', String(!video.muted));
    sound.setAttribute('aria-label', video.muted ? 'Turn the sound on' : 'Turn the sound off');
    start.hidden = started || wantsPlay;
  };
  const play = () => {
    if (!wantsPlay || !onScreen) return;
    const attempt = video.play();
    // NotAllowedError is the browser refusing to autoplay (Low Power Mode,
    // data saver): offer the button. AbortError only means a pause() - the
    // off-screen observer's first report, say - interrupted the request.
    if (attempt) attempt.catch(error => { if (error.name === 'NotAllowedError') { wantsPlay = false; render(); } });
  };

  video.addEventListener('playing', () => { started = true; render(); });
  pause.addEventListener('click', () => { wantsPlay = !wantsPlay; if (wantsPlay) play(); else video.pause(); render(); });
  start.addEventListener('click', () => { wantsPlay = true; play(); render(); });
  sound.addEventListener('click', () => {
    video.muted = !video.muted;
    if (!video.muted && !wantsPlay) { wantsPlay = true; play(); }
    render();
  });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(([entry]) => {
      onScreen = entry.isIntersecting;
      if (onScreen) play(); else video.pause();
    }, { threshold: 0.25 }).observe(video);
  }
  film.querySelector('.film-controls').hidden = false;
  if (wantsPlay) video.preload = 'auto';
  render(); play();
}

// The collections rail: every collection, scrolling sideways (2026-09-24). A
// finger or a trackpad scrolls it natively. A mouse has no sideways wheel, so
// it gets both: the rail drags like a finger, and two arrows step through it.
// The arrows appear only when this script runs and the rail is wider than the
// window, and each greys out at its end of the rail.
(() => {
  const rail = document.querySelector('.collection-rail');
  const arrows = document.querySelector('.rail-arrows');
  if (!rail || !arrows) return;
  const prev = arrows.querySelector('[data-rail="prev"]');
  const next = arrows.querySelector('[data-rail="next"]');
  const calm = window.matchMedia('(prefers-reduced-motion: reduce)');
  const note = (...detail) => document.dispatchEvent(new CustomEvent('postmello:event', { detail }));
  const sync = () => {
    arrows.hidden = rail.scrollWidth <= rail.clientWidth + 4;
    prev.disabled = rail.scrollLeft <= 4;
    next.disabled = rail.scrollLeft + rail.clientWidth >= rail.scrollWidth - 4;
    if (!prev.disabled) note('rail', 'scrolled');
    if (next.disabled && !prev.disabled) note('rail', 'end');
  };
  const move = direction => rail.scrollBy({
    left: direction * rail.clientWidth * 0.8,
    behavior: calm.matches ? 'auto' : 'smooth',
  });
  prev.addEventListener('click', () => move(-1));
  next.addEventListener('click', () => move(1));
  // Snapping is off while dragging, or it fights the hand.
  let drag = null;
  rail.addEventListener('pointerdown', event => {
    if (event.pointerType !== 'mouse' || event.button !== 0) return;
    drag = { x: event.clientX, left: rail.scrollLeft };
    rail.setPointerCapture(event.pointerId);
    rail.classList.add('is-dragging');
  });
  rail.addEventListener('pointermove', event => {
    if (drag) rail.scrollLeft = drag.left - (event.clientX - drag.x);
  });
  const drop = () => { drag = null; rail.classList.remove('is-dragging'); };
  rail.addEventListener('pointerup', drop);
  rail.addEventListener('pointercancel', drop);
  rail.addEventListener('dragstart', event => event.preventDefault());
  rail.addEventListener('scroll', sync, { passive: true });
  new ResizeObserver(sync).observe(rail);
  sync();
})();

// The opening header scrolls away naturally. Reuse the same navigation as a
// fixed white bar only after the entire hero has passed.
const headerPosition = document.querySelector('.header-position');
const opening = document.querySelector('.opening');
if (headerPosition && opening) {
  // Two heights, because the bar is two different sizes and they mean
  // different things. --nav-height is the OPENING lockup, and .opening reserves
  // exactly that much padding for it; --nav-dock-height is the shorter docked
  // strip, and it is what an anchor has to clear. Writing the docked height
  // into --nav-height would shrink .opening's padding by the difference while
  // the reader is a screen or two below it, which yanks the whole page up.
  const measureHeader = () => {
    const docked = headerPosition.classList.contains('is-docked');
    const property = docked ? '--nav-dock-height' : '--nav-height';
    document.documentElement.style.setProperty(property, `${headerPosition.offsetHeight}px`);
  };
  measureHeader();
  new ResizeObserver(measureHeader).observe(headerPosition);
  new IntersectionObserver(([entry]) => {
    headerPosition.classList.toggle('is-docked', entry.boundingClientRect.bottom <= 0);
    // The ResizeObserver catches the size change on its own, but only on the
    // FIRST dock - re-docking at an unchanged size fires nothing, and the
    // desk section's height cap reads --nav-dock-height on every layout.
    measureHeader();
  }, { threshold: 0 }).observe(opening);
}

const menuButton = document.querySelector('.menu-toggle');
const mainNavigation = document.getElementById('main-navigation');
if (menuButton && mainNavigation) {
  const header = menuButton.closest('.header, .site-head');
  const setMenuOpen = (open) => {
    header.classList.toggle('is-menu-open', open);
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  };
  header.classList.add('has-menu');
  menuButton.hidden = false;
  menuButton.addEventListener('click', () => setMenuOpen(menuButton.getAttribute('aria-expanded') !== 'true'));
  mainNavigation.addEventListener('click', event => {
    if (event.target.closest('a')) setMenuOpen(false);
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menuButton.getAttribute('aria-expanded') === 'true') {
      setMenuOpen(false);
      menuButton.focus();
    }
  });
  document.addEventListener('click', event => {
    if (!header.contains(event.target)) setMenuOpen(false);
  });
  header.addEventListener('focusout', event => {
    if (!header.contains(event.relatedTarget)) setMenuOpen(false);
  });
  window.matchMedia('(max-width:760px)').addEventListener('change', () => setMenuOpen(false));
}

// Keep previously shared homepage section links useful after the redesign.
if (opening) {
  const aliases = {'#how-it-works':'#experience', '#desk':'#experience', '#membership':'#pricing', '#grandparents':'#family', '#safety':'#parents', '#request-an-invite':'#pricing', '#get-the-link':'#experience'};
  if (aliases[location.hash]) location.replace(aliases[location.hash]);
}

// Anonymous page events: which sections were reached, how long the page stayed
// in view, and what was tapped. Each event is one request to /t/<page>/<event>,
// answered by functions/t/[[path]].js and counted by Cloudflare's request log,
// so there is no cookie, no identifier and nothing kept in the browser. Each
// event is sent at most once per page load. It can never break the page: every
// part is optional and a failed send is dropped. scripts/site-events.py reads it.
(() => {
  try {
    const slug = value => String(value).toLowerCase().replace(/\.html$/, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
    const page = slug(location.pathname) || 'home';
    const sent = new Set();
    const send = (...parts) => {
      const path = `/t/${page}/${parts.map(slug).filter(Boolean).join('/')}`;
      if (sent.has(path)) return;
      sent.add(path);
      try { if (navigator.sendBeacon && navigator.sendBeacon(path)) return; } catch (_) {}
      fetch(path, { method: 'POST', keepalive: true }).catch(() => {});
    };
    const sectionName = element => {
      const section = element && element.closest('section, footer, header');
      if (!section) return 'page';
      return section.id || (section.tagName === 'SECTION' ? section.classList[0] : section.tagName) || 'page';
    };

    send('view');
    document.addEventListener('postmello:event', event => send(...event.detail));

    // A section counts as reached once any of it is in the top half of the screen.
    if ('IntersectionObserver' in window) {
      const reached = new IntersectionObserver(entries => entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        reached.unobserve(entry.target);
        send('seen', sectionName(entry.target).replace(/-section$/, ''));
      }), { rootMargin: '0px 0px -50% 0px' });
      document.querySelectorAll('main section, footer').forEach(section => reached.observe(section));
    }

    // Time the page was actually on screen, as milestones. A milestone is sent
    // while the visitor is still here, so it never depends on the in-app
    // browsers firing anything on the way out, which they often do not.
    const marks = [10, 30, 60, 120, 300];
    let seconds = 0;
    const clock = setInterval(() => {
      if (document.visibilityState !== 'visible') return;
      seconds += 5;
      if (marks.includes(seconds)) send('time', `${seconds}s`);
      if (seconds >= marks[marks.length - 1]) clearInterval(clock);
    }, 5000);

    document.addEventListener('click', event => {
      const link = event.target.closest('a[href]');
      if (link) {
        const url = new URL(link.href, location.href);
        const name = link.dataset.brandHref === 'app_store_url' || url.hostname === 'apps.apple.com' ? 'app-store'
          : url.hostname.endsWith('instagram.com') ? 'instagram'
          : url.origin !== location.origin ? url.hostname
          : url.pathname === location.pathname && url.hash ? `jump-${url.hash}`
          : url.pathname === '/' ? 'home' : url.pathname;
        send('tap', name, sectionName(link));
        return;
      }
      if (event.target.closest('.film-pause') && video && !video.paused) send('video', 'paused');
    }, true);

    // The film starts on its own, so "playing" says autoplay worked, not that
    // someone pressed anything; "watched" is reaching the bee's pickup once.
    const video = document.getElementById('desk-video');
    if (video) {
      video.addEventListener('playing', () => send('video', 'playing'));
      video.addEventListener('timeupdate', () => { if (video.currentTime >= 12.4) send('video', 'watched'); });
      video.addEventListener('volumechange', () => { if (!video.muted) send('video', 'sound'); });
    }
  } catch (_) {}
})();
