/* script.js – loads artifacts.xml and reveals cards on scroll           */
/* Works in browsers, GitHub Pages, and local dev server (http://…).     */

document.addEventListener('DOMContentLoaded', () => {
  fetch('artifacts.xml')
    .then(r => r.text())
    .then(xmlString => new DOMParser().parseFromString(xmlString, 'application/xml'))
    .then(xml => buildCards(xml))
    .then(initRevealOnScroll)
    .catch(err => console.error('Portfolio loader error →', err));
});

/* ------------------------------------------------------------------ */

function buildCards(xml) {
  const container = document.getElementById('artifacts');

  xml.querySelectorAll('artifact').forEach(node => {
    const grab = tag => node.querySelector(tag)?.textContent.trim() || '';

    // XML → variables
    const id    = node.getAttribute('id') || '';
    const title = grab('title');
    const intro = grab('introduction');
    const desc  = grab('description');
    const obj   = grab('objective');
    const proc  = grab('process');
    const tools = grab('tools');
    const vp    = grab('valueProposition');
    const uv    = grab('uniqueValue');
    const rel   = grab('relevance');
    const img   = grab('image');

    /* -------- references (can contain raw <a> tag) -------- */
    const refEl   = node.querySelector('references');
    const refsHTML = refEl
      ? new XMLSerializer().serializeToString(refEl).replace(/^<references>|<\/references>$/g, '')
      : '';

    /* -------- build card HTML -------- */
    const card = document.createElement('article');
    card.className = 'artifact';
    card.innerHTML = `
      ${img ? `<img src="${img}" alt="${title} preview" class="artifact-img">` : ''}
      <h2>${id}: ${title}</h2>
      <section><strong>Introduction:</strong> ${intro}</section>
      <section><strong>Description:</strong> ${desc}</section>
      <section><strong>Objective:</strong> ${obj}</section>
      <section><strong>Process:</strong> ${proc}</section>
      <section><strong>Tools & Tech used:</strong> ${tools}</section>
      <section><strong>Value Proposition:</strong> ${vp}</section>
      <section><strong>Unique Value:</strong> ${uv}</section>
      <section><strong>Relevance:</strong> ${rel}</section>
      <section class="refs">${refsHTML}</section>
    `;
    container.appendChild(card);
  });
}

/* ------------------------------------------------------------------ */
/* Intersection Observer reveal                                       */

function initRevealOnScroll() {
  const cards = document.querySelectorAll('.artifact');
  const io = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('show');
          io.unobserve(entry.target);   // animate once
        }
      });
    },
    { threshold: 0.15 }
  );

  cards.forEach(c => io.observe(c));
}

