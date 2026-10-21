(() => {
  'use strict';
  const tools = document.querySelector('.publication-tools');
  const search = document.querySelector('#publication-search');
  const groups = [...document.querySelectorAll('.publication-group')];
  const papers = [...document.querySelectorAll('.publication')];
  const buttons = [...document.querySelectorAll('[data-filter]')];
  let filter = 'all';
  const apply = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    for (const group of groups) {
      let shown = 0;
      for (const paper of group.querySelectorAll('.publication')) {
        const match = (filter === 'all' || group.dataset.group === filter)
          && paper.textContent.toLocaleLowerCase().includes(query);
        paper.hidden = !match;
        if (match) { shown++; count++; }
      }
      group.hidden = shown === 0;
    }
    document.querySelector('#publication-count').textContent = `${count} of ${papers.length} publications`;
    document.querySelector('.empty-state').hidden = count !== 0;
    document.querySelector('.cofirst-note').hidden = !groups.some(g => !g.hidden && g.dataset.group === 'published');
  };
  if (tools && search) {
    tools.hidden = false;
    buttons.forEach(button => button.addEventListener('click', () => {
      filter = button.dataset.filter;
      buttons.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
      apply();
    }));
    search.addEventListener('input', apply);
    apply();
  }
  if ('IntersectionObserver' in window) {
    const navLinks = [...document.querySelectorAll('.profile nav a')];
    const observer = new IntersectionObserver(entries => {
      const current = entries.find(entry => entry.isIntersecting);
      if (!current) return;
      navLinks.forEach(a => {
        if (a.hash === `#${current.target.id}`) a.setAttribute('aria-current', 'location');
        else a.removeAttribute('aria-current');
      });
    }, { rootMargin: '0px 0px -65% 0px', threshold: 0 });
    document.querySelectorAll('.content-section h2').forEach(h => observer.observe(h));
  }
})();
