document.addEventListener('DOMContentLoaded', function() {
  fetch('artifacts.xml')
    .then(response => response.text())
    .then(data => {
      const parser = new DOMParser();
      const xml = parser.parseFromString(data, 'application/xml');
      const artifacts = xml.querySelectorAll('artifact');
      const container = document.getElementById('artifacts');

      artifacts.forEach(art => {
        const id = art.getAttribute('id');
        const title = art.querySelector('title').textContent;
        const intro = art.querySelector('introduction').textContent;
        const desc = art.querySelector('description').textContent;
        const obj = art.querySelector('objective').textContent;
        const process = art.querySelector('process').textContent;
        const tools = art.querySelector('tools').textContent;
        const vp = art.querySelector('valueProposition').textContent;
        const uv = art.querySelector('uniqueValue').textContent;
        const rel = art.querySelector('relevance').textContent;
        const refs = art.querySelector('references').innerHTML;

        const artDiv = document.createElement('div');
        artDiv.classList.add('artifact');
        artDiv.innerHTML = `
          <h2>${id}: ${title}</h2>
          <section><strong>Introduction:</strong> ${intro}</section>
          <section><strong>Description:</strong> ${desc}</section>
          <section><strong>Objective:</strong> ${obj}</section>
          <section><strong>Process:</strong> ${process}</section>
          <section><strong>Tools & Tech used:</strong> ${tools}</section>
          <section><strong>Value Proposition:</strong> ${vp}</section>
          <section><strong>Unique Value:</strong> ${uv}</section>
          <section><strong>Relevance:</strong> ${rel}</section>
          <section><strong>References:</strong> ${refs}</section>
        `;
        container.appendChild(artDiv);
      });
    })
    .catch(err => console.error('Error loading artifacts.xml', err));
});

