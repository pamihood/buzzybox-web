const options = document.querySelectorAll('.desk-options button');
options.forEach(button => button.addEventListener('click', () => {
  options.forEach(option => option.setAttribute('aria-pressed', String(option === button)));
  const image = document.getElementById('desk-image');
  image.src = button.dataset.image;
  image.alt = button.dataset.alt;
  document.getElementById('desk-label').textContent = button.dataset.label;
}));

const heroKey = new URLSearchParams(window.location.search).get('hero');
const heroChoice = window.POSTMELLO_HERO_OPTIONS.find(option => option.key === heroKey);
if (heroChoice) {
  const title = document.getElementById('hero-title');
  const emphasis = document.createElement('em');
  emphasis.textContent = heroChoice.lines[1];
  title.replaceChildren(document.createTextNode(heroChoice.lines[0]), document.createElement('br'), emphasis);
  document.getElementById('hero-description').textContent = heroChoice.description;
  document.title = 'Postmello — ' + heroChoice.lines.join(' ');
}


// The opening header scrolls away naturally. Reuse the same navigation as a
// fixed white bar only after the entire hero has passed.
const headerPosition = document.querySelector('.header-position');
const opening = document.querySelector('.opening');
if (headerPosition && opening) {
  const measureHeader = () => {
    document.documentElement.style.setProperty('--nav-height', `${headerPosition.offsetHeight}px`);
  };
  measureHeader();
  new ResizeObserver(measureHeader).observe(headerPosition);
  new IntersectionObserver(([entry]) => {
    headerPosition.classList.toggle('is-docked', entry.boundingClientRect.bottom <= 0);
  }, { threshold: 0 }).observe(opening);
}

const menuButton = document.querySelector('.menu-toggle');
const mainNavigation = document.getElementById('main-navigation');
if (menuButton && mainNavigation) {
  const header = menuButton.closest('.header');
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
