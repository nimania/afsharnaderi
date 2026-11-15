(() => {
  const input = document.getElementById('search');
  const select = document.getElementById('category');
  const items = [...document.querySelectorAll('.resource')];
  const none = document.getElementById('no-results');
  if (!input || !select || !none) return;
  const normalize = (text) => text.normalize('NFKC').replace(/ي/g, 'ی').replace(/ك/g, 'ک').toLocaleLowerCase('fa');
  const refresh = () => {
    const query = normalize(input.value.trim());
    let count = 0;
    for (const item of items) {
      const matches = normalize(item.textContent || '').includes(query) && (select.value === 'all' || item.dataset.category === select.value);
      item.hidden = !matches;
      if (matches) count++;
    }
    none.hidden = count > 0;
  };
  input.addEventListener('input', refresh);
  select.addEventListener('change', refresh);
})();