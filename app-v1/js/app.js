const $ = (s) => document.querySelector(s);
const pos = (angle, ring) => {
  const rad = (angle * Math.PI) / 180;
  const r = ring === 1 ? 38 : 0;
  return { x: 50 + Math.cos(rad) * r, y: 46 + Math.sin(rad) * r };
};
const areaClass = (area) => 'area-' + String(area).replace(/[^a-zA-Z0-9]+/g, '-').replace(/^-|-$/g, '');
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let nodes = [], edges = [], quick = [];
let current = null;

async function load() {
  [nodes, edges, quick] = await Promise.all([
    fetch('./data/nodes.json').then(r => r.json()),
    fetch('./data/edges.json').then(r => r.json()),
    fetch('./data/quick-links.json').then(r => r.json())
  ]);
  current = nodes.find(n => n.id === 'CORE') || nodes[0];
  renderFilters();
  renderQuickLinks();
  renderMap();
  renderLegend();
  renderDetail(current);
}

function renderFilters() {
  const areas = [...new Set(nodes.map(n => n.area).filter(Boolean))].sort();
  $('#area').innerHTML = '<option value="all">All areas</option>' + areas.map(a => `<option>${esc(a)}</option>`).join('');
}

function renderQuickLinks() {
  $('#quick').innerHTML = quick.map(q => `<a href="${esc(q.url)}" target="_blank" rel="noopener">${esc(q.label)}</a>`).join('');
}

function brainSvg() {
  return `<svg viewBox="0 0 320 230" aria-hidden="true">
    <defs><radialGradient id="brainGlow" cx="50%" cy="38%" r="70%"><stop offset="0" stop-color="#c7ffff"/><stop offset=".38" stop-color="#208cff"/><stop offset="1" stop-color="#08284a"/></radialGradient></defs>
    <path d="M50 125 C16 97 36 50 80 52 C96 8 151 17 162 54 C204 6 272 42 250 91 C305 106 286 184 225 181 C200 222 128 215 116 177 C73 201 23 166 50 125Z" fill="url(#brainGlow)" stroke="#86f4ff" stroke-width="6"/>
    <path d="M76 92 C116 72 128 116 161 101 C196 87 200 58 230 78 M72 137 C112 121 125 165 160 145 C198 129 203 170 234 148 M126 57 C118 86 143 91 163 101 M177 52 C170 84 190 95 218 91" fill="none" stroke="#e8ffff" stroke-width="5" opacity=".72" stroke-linecap="round"/>
    <circle cx="78" cy="92" r="5" fill="#eaffff"/><circle cx="230" cy="78" r="5" fill="#eaffff"/><circle cx="72" cy="137" r="5" fill="#eaffff"/><circle cx="234" cy="148" r="5" fill="#eaffff"/><circle cx="162" cy="101" r="6" fill="#eaffff"/>
  </svg>`;
}

function filteredNodes() {
  const q = $('#search').value.toLowerCase();
  const area = $('#area').value;
  return nodes.filter(n => n.id !== 'CORE' && (area === 'all' || n.area === area) && [n.id,n.title,n.area,n.type,n.status].join(' ').toLowerCase().includes(q));
}

function renderMap() {
  const visible = filteredNodes();
  const map = $('#dashboard');
  const core = nodes.find(n => n.id === 'CORE');
  map.querySelectorAll('.node,.brain').forEach(el => el.remove());
  map.insertAdjacentHTML('beforeend', `<a class="brain" href="${esc(core.mainLink)}" target="_blank" rel="noopener" data-id="CORE">${brainSvg()}<div class="brainLabel"><small>START HERE</small>ZOZ External Brain</div></a>`);
  const nodeHtml = visible.map(n => {
    const p = pos(n.angle, n.ring);
    return `<a class="node ${areaClass(n.area)}" href="${esc(n.mainLink)}" target="_blank" rel="noopener" style="--x:${p.x}%;--y:${p.y}%" data-id="${esc(n.id)}" title="${esc(n.title)}">
      <div><div class="dot"></div><small>${esc(n.id)}</small><strong>${esc(n.title)}</strong></div>
    </a>`;
  }).join('');
  map.insertAdjacentHTML('beforeend', nodeHtml);
  drawLines(visible);
  bindHover();
}

function drawLines(visible) {
  const lineSvg = $('#lines');
  const visibleIds = new Set(visible.map(n => n.id));
  const paths = visible.map(n => {
    const p = pos(n.angle, n.ring);
    return `<path data-to="${esc(n.id)}" d="M 50 46 C ${50 + (p.x-50)*0.35} ${46 + (p.y-46)*0.1}, ${50 + (p.x-50)*0.65} ${46 + (p.y-46)*0.9}, ${p.x} ${p.y}" />`;
  }).join('') + edges.filter(e => visibleIds.has(e.from) && visibleIds.has(e.to)).map(e => {
    const a = nodes.find(n => n.id === e.from), b = nodes.find(n => n.id === e.to);
    const pa = pos(a.angle,a.ring), pb = pos(b.angle,b.ring);
    return `<path data-to="${esc(e.to)}" d="M ${pa.x} ${pa.y} Q 50 46 ${pb.x} ${pb.y}" />`;
  }).join('');
  lineSvg.innerHTML = `<defs><linearGradient id="grad"><stop offset="0" stop-color="#58e5ff"/><stop offset=".5" stop-color="#bd85ff"/><stop offset="1" stop-color="#ffbd55"/></linearGradient></defs>${paths}`;
}

function bindHover() {
  document.querySelectorAll('.node,.brain').forEach(el => {
    el.addEventListener('mouseenter', () => preview(el.dataset.id, true));
    el.addEventListener('focus', () => preview(el.dataset.id, true));
    el.addEventListener('touchstart', () => preview(el.dataset.id, true), {passive:true});
  });
}

function preview(id, hot) {
  const n = nodes.find(x => x.id === id) || current;
  current = n;
  renderDetail(n);
  document.querySelectorAll('.lineLayer path').forEach(p => p.classList.toggle('hot', hot && p.dataset.to === id));
}

function renderDetail(n) {
  $('#detail').innerHTML = `<div><div class="kicker">Selected source</div><h2>${esc(n.title)}</h2><p>${esc(n.nextAction)}</p><span class="pill">${esc(n.id)}</span><span class="pill">${esc(n.area)}</span><span class="pill">${esc(n.confidence)}</span></div><a class="openBtn" href="${esc(n.mainLink)}" target="_blank" rel="noopener">Open file</a>`;
}

function renderLegend() {
  const groups = [...new Map(nodes.filter(n=>n.id!=='CORE').map(n => [n.area,n])).values()];
  $('#legend').innerHTML = groups.map(n => `<div class="legendItem ${areaClass(n.area)}"><b>${esc(n.area)}</b><span>${esc(n.type)} · ${esc(n.status)}</span></div>`).join('');
}

$('#search').addEventListener('input', renderMap);
$('#area').addEventListener('change', renderMap);
load().catch(err => {
  $('#dashboard').innerHTML = `<div class="detail"><h2>Could not load dashboard data</h2><p>${esc(err.message)}</p></div>`;
});
