const menu = document.querySelector('.menu-toggle');
const nav = document.querySelector('#navigation');
menu?.addEventListener('click', () => {
  const expanded = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(expanded));
  nav.classList.toggle('open', expanded);
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menu?.getAttribute('aria-expanded') === 'true') {
    menu.setAttribute('aria-expanded', 'false');
    nav.classList.remove('open');
    menu.focus();
  }
});
for (const section of document.querySelectorAll('[data-filter-section]')) {
  const items = [...section.querySelectorAll('[data-category]')];
  const buttons = [...section.querySelectorAll('[data-filter]')];
  const search = section.querySelector('input[type=search]');
  let category = 'All';
  const update = () => {
    const query = (search?.value || '').trim().toLocaleLowerCase();
    let visible = 0;
    for (const item of items) {
      item.hidden = !(category === 'All' || item.dataset.category === category) || !item.dataset.search.toLocaleLowerCase().includes(query);
      if (!item.hidden) visible++;
    }
    const noun = search ? 'publication' : 'project';
    section.querySelector('.results-count').textContent = `${visible} ${noun}${visible === 1 ? '' : 's'}`;
    section.querySelector('.empty').hidden = visible !== 0;
  };
  for (const button of buttons) button.addEventListener('click', () => {
    category = button.dataset.filter;
    for (const other of buttons) other.setAttribute('aria-pressed', String(other === button));
    update();
  });
  search?.addEventListener('input', update);
}
