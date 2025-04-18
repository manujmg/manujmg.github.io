/* script.js – final version with background‑image cards */

document.addEventListener('DOMContentLoaded', () => {
  fetch('artifacts.xml')
    .then(r => r.text())
    .then(xmlStr => new DOMParser().parseFromString(xmlStr, 'application/xml'))
    .then(xml => buildCards(xml))        // build DOM
    .then(initRevealOnScroll)            // wire up observer
    .catch(err => console.error('Portfolio loader error →', err));
});

/* ------------------------------------------------------------------ */

function buildCards(xml){
  const container = document.getElementById('artifacts');

  xml.querySelectorAll('artifact').forEach(node => {
    const g = tag => node.querySelector(tag)?.textContent.trim() || '';

    /* pull data --------------------------------------------------- */
    const id    = node.getAttribute('id') || '';
    const title = g('title');
    const intro = g('introduction');
    const desc  = g('description');
    const obj   = g('objective');
    const proc  = g('process');
    const tools = g('tools');
    const vp    = g('valueProposition');
    const uv    = g('uniqueValue');
    const rel   = g('relevance');
    const img   = g('image');

    /* serialize <references> to preserve internal <a> tag(s) ---- */
    const refHTML = node.querySelector('references')
      ? new XMLSerializer()
          .serializeToString(node.querySelector('references'))
          .replace(/^<references>|<\/references>$/g,'')
      : '';

    /* build card -------------------------------------------------- */
    const card = document.createElement('article');
    card.className = 'artifact';
    card.style.backgroundImage = `url('${img}')`;

    card.innerHTML = `
      <div class="artifact-content">
        <h2>${id}: ${title}</h2>

        <section><strong>Introduction:</strong> ${intro}</section>
        <section><strong>Description:</strong> ${desc}</section>
        <section><strong>Objective:</strong> ${obj}</section>
        <section><strong>Process:</strong> ${proc}</section>
        <section><strong>Tools & Tech used:</strong> ${tools}</section>
        <section><strong>Value Proposition:</strong> ${vp}</section>
        <section><strong>Unique Value:</strong> ${uv}</section>
        <section><strong>Relevance:</strong> ${rel}</section>

        <section class="refs">${refHTML}</section>
      </div>
    `;
    container.appendChild(card);
  });
}

/* reveal‑on‑scroll ----------------------------------------------- */
function initRevealOnScroll(){
  const cards = document.querySelectorAll('.artifact');
  const io = new IntersectionObserver(entries=>{
    entries.forEach(entry=>{
      if(entry.isIntersecting){
        entry.target.classList.add('show');
        io.unobserve(entry.target);
      }
    });
  },{threshold:0.15});

  cards.forEach(c=>io.observe(c));
}

