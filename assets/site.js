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

// "Not on your iPad?": email yourself the App Store link. Postmello is
// iPad-only and the ads bring parents holding phones. The form lives in the
// closing section - never the hero, which only gets one quiet line jumping
// down to it. On a phone the form takes the closing badge's place
// (html.send-link-first); on a computer or another tablet it sits under the
// badge; on an iPad neither appears - the badge is the right answer there.
// Without this script both stay hidden and the badge is all there is.
//
// Cloudflare Turnstile guards the endpoint, as it guarded the old invite form,
// but its script loads only once someone starts on the form: nobody who merely
// reads the page fetches anything from Cloudflare's challenge servers. It runs
// "interaction-only", so it is invisible unless Cloudflare wants a click.
(() => {
  const panels = [...document.querySelectorAll('[data-send-link]')];
  if (!panels.length) return;
  const ua = navigator.userAgent;
  // iPadOS Safari reports itself as a Mac; the touch points give it away.
  const onIPad = /iPad/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  if (onIPad) return;
  const onPhone = /iPhone|iPod|Android.+Mobile|Windows Phone/i.test(ua);
  document.documentElement.classList.toggle('send-link-first', onPhone);
  const local = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  const note = (...parts) => document.dispatchEvent(new CustomEvent('postmello:event', { detail: parts }));

  let turnstile;
  const loadTurnstile = () => turnstile || (turnstile = new Promise((resolve, reject) => {
    window.postmelloTurnstileReady = () => resolve(window.turnstile);
    const script = document.createElement('script');
    script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=postmelloTurnstileReady';
    script.async = true;
    script.onerror = reject;
    document.head.append(script);
  }));

  const EMAIL = /^[^\s@]{1,64}@[^\s@.]+(\.[^\s@.]+)+$/;
  const TICK = 'Tick the box to confirm, and it will send.';
  const showDone = () => panels.forEach(panel => {
    panel.querySelector('.send-link-form').hidden = true;
    panel.querySelector('.send-link-done').hidden = false;
  });

  panels.forEach(panel => {
    const form = panel.querySelector('.send-link-form');
    const input = form.querySelector('input[type=email]');
    const button = form.querySelector('button[type=submit]');
    const message = form.querySelector('.send-link-msg');
    const check = form.querySelector('.send-link-check');
    // Cloudflare's always-pass test key and a local stand-in on a dev server:
    // the real key only answers on postmello.com.
    const sitekey = local ? '1x00000000000000000000AA' : panel.dataset.sitekey;
    const endpoint = local ? '/mock/ipad-link' : panel.dataset.endpoint;
    let widget = null;
    let token = '';
    let waiting = null;
    // True while Cloudflare is showing its "Verify you are human" box: then the
    // form waits for the tick, however long it takes, instead of giving up.
    let asking = false;

    const prepare = () => {
      if (widget !== null) return;
      widget = false;
      note('link', 'start', panel.dataset.sendLink);
      loadTurnstile().then(api => {
        widget = api.render(check, {
          sitekey, appearance: 'interaction-only', size: 'flexible',
          callback: value => { token = value; if (waiting) { message.textContent = ''; waiting(value); } },
          'expired-callback': () => { token = ''; },
          'error-callback': () => { token = ''; },
          'before-interactive-callback': () => { asking = true; if (waiting) message.textContent = TICK; },
          'after-interactive-callback': () => { asking = false; },
        });
      }).catch(() => { widget = null; });
    };
    form.addEventListener('focusin', prepare);
    form.addEventListener('pointerdown', prepare);

    // The token usually lands while the address is typed. If Cloudflare is
    // asking for a tick, wait for the person - the send goes on its own once
    // they tick. Otherwise give it 20 seconds (a blocked script, say) and say
    // it did not send. Found on the live page 2026-09-22: a challenged browser
    // got the error under a box it had not had the chance to tick.
    const tokenReady = () => token ? Promise.resolve(token) : new Promise(resolve => {
      waiting = value => { waiting = null; resolve(value); };
      if (asking) message.textContent = TICK;
      const giveUp = () => {
        if (!waiting) return;
        if (asking) { setTimeout(giveUp, 20000); return; }
        waiting = null; resolve('');
      };
      setTimeout(giveUp, 20000);
    });

    form.addEventListener('submit', async event => {
      event.preventDefault();
      message.textContent = '';
      const email = input.value.trim();
      if (!EMAIL.test(email)) { message.textContent = 'Check the email address and try again.'; input.focus(); return; }
      prepare();
      button.disabled = true;
      button.textContent = 'Sending…';
      const done = text => { button.disabled = false; button.textContent = 'Email me the link'; message.textContent = text || ''; };
      const proof = await tokenReady();
      if (!proof) { done('That didn’t send. Please try again in a moment.'); return; }
      try {
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, company: form.company.value, turnstileToken: proof, source: panel.dataset.sendLink }),
        });
        const reply = await response.json().catch(() => ({}));
        if (response.ok && reply.status === 'ok') { note('link', 'sent', panel.dataset.sendLink); showDone(); return; }
        // A Turnstile token is single-use: whatever happened, the next try needs a fresh one.
        token = '';
        if (window.turnstile && widget) window.turnstile.reset(widget);
        done(reply.status === 'invalid_email' ? 'Check the email address and try again.' : 'That didn’t send. Please try again in a moment.');
      } catch (_) {
        token = '';
        if (window.turnstile && widget) window.turnstile.reset(widget);
        done('That didn’t send. Please try again in a moment.');
      }
    });
    panel.hidden = false;
  });

  const cue = document.querySelector('.send-link-cue');
  if (cue) {
    cue.hidden = false;
    cue.addEventListener('click', event => {
      const target = document.getElementById('get-the-link');
      if (!target) return;
      event.preventDefault();
      note('link', 'cue');
      // Centred rather than under the docked bar, and the cursor goes in the
      // field only once the scroll has landed: focusing mid-scroll cancels a
      // smooth scroll, which stranded the form at the foot of a phone screen.
      const calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      target.scrollIntoView({ behavior: calm ? 'auto' : 'smooth', block: 'center' });
      // Pictures further up load as the scroll passes them and push the form
      // down after the scroll has aimed at it (several have no reserved size),
      // so once it lands, look again and step straight to it if it moved.
      const input = target.querySelector('input[type=email]');
      let settled = false;
      const settle = () => {
        if (settled) return;
        settled = true;
        const box = target.getBoundingClientRect();
        if (box.top < 0 || box.bottom > window.innerHeight) target.scrollIntoView({ block: 'center' });
        if (input) input.focus({ preventScroll: true });
      };
      window.addEventListener('scrollend', settle, { once: true });
      setTimeout(settle, 1500);
    });
  }
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
  const aliases = {'#how-it-works':'#experience', '#desk':'#experience', '#membership':'#pricing', '#grandparents':'#family', '#safety':'#parents', '#request-an-invite':'#pricing'};
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
