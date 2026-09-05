const options = document.querySelectorAll('.desk-options button');
options.forEach(button => button.addEventListener('click', () => {
  options.forEach(option => option.setAttribute('aria-pressed', String(option === button)));
  const image = document.getElementById('desk-image');
  image.src = '/assets/' + button.dataset.image;
  image.alt = button.dataset.alt;
  document.getElementById('desk-label').textContent = button.dataset.label;
}));
