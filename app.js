const byId = id => document.getElementById(id);
const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g,
  character => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[character]));
const filters = ['search', 'category', 'type', 'location', 'status'];
const regions = ['전체', '한국', '미국', '영국', '유럽', '일본', '태국', '호주', '국제'];
const sections = {
  home: ['최근 기회', '공식 출처에서 확인한 채용과 공모를 살펴보세요.'],
  jobs: ['채용·외주', '공고의 근무 방식, 지원 가능 지역, 비자 조건을 확인하세요.'],
  opportunities: ['공모·지원금', '창작지원과 공모전 기회를 찾아보세요.'],
  events: ['학회·행사', '행사 일정과 발표 접수 마감일을 확인하세요.'],
  community: ['국내외 학회·커뮤니티', '의료미술과 시각화 관련 전문 단체를 찾아보세요.'],
  saved: ['나의 관심 목록', '이 브라우저에 저장한 항목입니다.'],
};
let page = 'home';
let region = '전체';
let sources = {};
let saved = new Set();
try {
  const entries = JSON.parse(localStorage.getItem('bvc-saved') || '[]');
  if (Array.isArray(entries)) saved = new Set(entries);
} catch {
  // Keep an in-memory list when local storage is unavailable.
}

function todayInKorea() {
  return new Intl.DateTimeFormat('sv-SE', {timeZone: 'Asia/Seoul'}).format(new Date());
}

function statusOf(item) {
  if (item.status) return item.status;
  if (!item.deadline || item.deadline === todayInKorea()) return '확인 필요';
  return item.deadline < todayInKorea() ? '마감' : '접수 예정 일정';
}

function link(url, label) {
  return typeof url === 'string' && url.startsWith('https://')
    ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${label} ↗</a>`
    : '<span class="small">출처 확인 필요</span>';
}

function card(item) {
  const job = item.id.startsWith('j-');
  const community = Boolean(item.name);
  return `<article class="card">
    <div class="cardtop"><h3>${escapeHtml(item.title || item.name)}</h3><span class="chip">${escapeHtml(item.type || item.region)}</span></div>
    <p>${escapeHtml([item.org || item.en, item.location || item.area].filter(Boolean).join(' · '))}</p>
    ${item.desc ? `<p>${escapeHtml(item.desc)}</p>` : ''}
    <div class="chips">
      ${community ? '' : `<span class="chip blue">${escapeHtml(statusOf(item))}</span>`}
      ${item.category ? `<span class="chip">${escapeHtml(item.category)}</span>` : ''}
      ${item.deadline ? `<span class="chip orange">마감 ${escapeHtml(item.deadline)}</span>` : ''}
    </div>
    ${job ? `<p class="small">근무 방식 · ${escapeHtml(item.work_mode || '확인 필요')}<br>한국 거주 상태로 근무 · ${escapeHtml(item.korea_eligible || '확인 필요')}<br>비자 지원 · ${escapeHtml(item.visa || '확인 필요')}</p>` : ''}
    ${item.last_checked ? `<p class="small">마지막 확인 ${escapeHtml(item.last_checked)}${item.source_url ? ` · ${link(item.source_url, '채용 보드')}` : ''}</p>` : ''}
    <div class="cardbottom">${link(item.url, community ? '단체 홈페이지' : '원문 보기')}
      <button class="save ${saved.has(item.id) ? 'saved' : ''}" data-save="${escapeHtml(item.id)}" aria-pressed="${saved.has(item.id)}">${saved.has(item.id) ? '★ 저장됨' : '☆ 저장'}</button>
    </div></article>`;
}

function render() {
  const listedSources = [
    ...(sources.greenhouse || []).map(item => ({...item, method: 'Greenhouse 자동 수집'})),
    ...(sources.lever || []).map(item => ({...item, method: 'Lever 자동 수집'})),
    ...(sources.manual || []).map(item => ({...item, method: '원문에서 확인'})),
  ];
  byId('sourceDirectory').classList.toggle('hidden', page !== 'jobs' || !listedSources.length);
  byId('sourceDirectory').innerHTML = `<details class="notice"><summary>국내외 채용 출처</summary><ul>${listedSources.map(item =>
    `<li>${link(item.url, escapeHtml(item.name))} · ${escapeHtml(item.region)} · ${escapeHtml(item.method)}</li>`).join('')}</ul></details>`;
  byId('regionbar').innerHTML = regions.map(value =>
    `<button data-region="${value}" class="${value === region ? 'active' : ''}" aria-pressed="${value === region}">${value}</button>`).join('');
  const sectionsData = {
    home: [...jobs.filter(item => item.status === '접수 중'), ...opportunities.filter(item => statusOf(item) !== '마감')],
    jobs,
    opportunities,
    events,
    community: communities.filter(item => region === '전체' || item.region === region),
    saved: [...jobs, ...opportunities, ...events, ...communities].filter(item => saved.has(item.id)),
  };
  let items = sectionsData[page];
  if (page === 'home' || page === 'jobs') {
    const [query, category, type, location, status] = filters.map(id => byId(id).value);
    items = items.filter(item =>
      [item.title, item.org, item.desc, item.category, ...(item.tags || [])].join(' ').toLowerCase().includes(query.trim().toLowerCase()) &&
      (!category || item.category === category) && (!type || item.type === type) &&
      (!location || item.region === location) && (!status || statusOf(item) === status));
    if (page === 'home') items = items.slice(0, 6);
  }
  byId('results').innerHTML = items.length ? items.map(card).join('') : '<div class="empty">표시할 항목이 없습니다.</div>';
  byId('jobcount').textContent = jobs.filter(item => item.status === '접수 중').length;
  byId('oppcount').textContent = opportunities.length + events.length;
  byId('orgcount').textContent = communities.length;
}

function showPage(next) {
  page = next;
  region = '전체';
  document.querySelectorAll('#nav [data-page]').forEach(button => {
    button.classList.toggle('active', button.dataset.page === page);
  });
  byId('hero').classList.toggle('hidden', page !== 'home');
  byId('metrics').classList.toggle('hidden', page !== 'home');
  byId('filters').classList.toggle('hidden', !['jobs', 'home'].includes(page));
  byId('regionbar').classList.toggle('hidden', page !== 'community');
  byId('savedHelp').classList.toggle('hidden', page !== 'saved');
  [byId('heading').textContent, byId('subheading').textContent] = sections[page];
  render();
  window.scrollTo({top: 0});
}

document.querySelectorAll('#nav [data-page]').forEach(button => {
  button.addEventListener('click', () => showPage(button.dataset.page));
});
filters.forEach(id => byId(id).addEventListener(id === 'search' ? 'input' : 'change', render));
byId('regionbar').addEventListener('click', event => {
  const button = event.target.closest('[data-region]');
  if (button) {
    region = button.dataset.region;
    render();
  }
});
byId('results').addEventListener('click', event => {
  const button = event.target.closest('[data-save]');
  if (!button) return;
  const id = button.dataset.save;
  if (saved.has(id)) saved.delete(id);
  else saved.add(id);
  try {
    localStorage.setItem('bvc-saved', JSON.stringify([...saved]));
  } catch {
    // The current session still retains the selection.
  }
  render();
  [...byId('results').querySelectorAll('[data-save]')].find(item => item.dataset.save === id)?.focus();
});

async function loadData() {
  const paths = ['data/jobs.json', 'data/opportunities.json', 'data/events.json', 'config/sources.json'];
  const results = await Promise.allSettled(paths.map(async (path, index) => {
    const response = await fetch(path);
    if (!response.ok) throw new Error(path);
    const data = await response.json();
    if (index < 3 && !Array.isArray(data)) throw new Error(path);
    return data;
  }));
  [jobs, opportunities, events] = results.slice(0, 3).map(result => result.value ?? []);
  sources = results[3].value ?? {};
  const notice = byId('loadNotice');
  if (results.some(result => result.status === 'rejected')) {
    notice.textContent = '일부 데이터를 불러오지 못했습니다. 잠시 후 새로고침해 주세요.';
    notice.classList.remove('hidden');
  }
  render();
}

showPage('home');
loadData();
