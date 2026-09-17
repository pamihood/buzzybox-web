const options = document.querySelectorAll('.desk-options button');
options.forEach(button => button.addEventListener('click', () => {
  options.forEach(option => option.setAttribute('aria-pressed', String(option === button)));
  const image = document.getElementById('desk-image');
  const video = document.getElementById('desk-video');
  // The original desk plays the film of a letter being made; the collections
  // are stills. Swapping which element is shown — rather than putting the
  // film somewhere else on the page — is what stops the same mint desk
  // appearing twice in one section. The poster is the film's own first frame,
  // and it is 4:3 like every still, so nothing shifts on the swap.
  if (video) {
    const wantsVideo = button.dataset.video === 'true';
    // Rewinding on the way out means coming back shows the film's first
    // frame — which is the poster, and is also what the collection stills
    // show — instead of dropping someone back onto a half-watched frame.
    if (!wantsVideo) { video.pause(); video.currentTime = 0; }
    video.hidden = !wantsVideo;
    image.hidden = wantsVideo;
  }
  image.src = button.dataset.image;
  image.alt = button.dataset.alt;
}));

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
  const aliases = {'#how-it-works':'#experience', '#desks':'#desk', '#membership':'#pricing', '#grandparents':'#family', '#safety':'#parents', '#request-an-invite':'#pricing'};
  if (aliases[location.hash]) location.replace(aliases[location.hash]);
}
