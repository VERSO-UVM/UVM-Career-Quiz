let pages = [];
let cur = 0;
let responses = {};
 
 
function buildPages(quiz) {
    const list = [];
    for (const category of quiz.categories) {
        for (const item of category.items) {
            list.push({ type: 'question', item });
        }
    }
    return list;
}
 

function updateFooter() {
    const total = pages.length;
    const answered = Object.values(responses).filter(v => v !== '' && v !== null && v !== undefined).length;
    const percent = total ? Math.round((answered / total) * 100) : 0;
    const remaining = pages.slice(cur).length;
 
    document.getElementById('footer-fill').style.width = percent + '%';
    document.getElementById('footer-label').textContent = `${answered} of ${total} question(s) answered`;
    document.getElementById('footer-remain').textContent =
        remaining > 0 ? `${remaining} remaining` : (total ? 'All done!' : '');
}
 
function renderQuestionPage(page) {
    const item = page.item;
    let body = '';
 
    if (item.type === 'mc') {
        const options = item.answer;
        if (!options.length) {
            body = `<p class="inline-note">No answer options have been defined yet.</p>`;
        } else {
            body = `<div class="options-list">` +
                options.map((option, i) => {
                    const label = option.text || `Option ${String.fromCharCode(65 + i)}`;
                    const sel = responses[item.id] === option.id;
                    return `<div class="radio-row${sel ? ' selected' : ''}" onclick="selectMC('${item.id}','${option.id}')">
            <div class="radio-circle"><div class="radio-dot"></div></div>
            <span class="radio-label">${esc(label)}</span>
          </div>`;
                }).join('') +
                `</div>`;
        }
    } else if (item.type === 'text') {
        const val = responses[item.id] || '';
        body = `<textarea class="open-textarea" placeholder="Type your answer here"
      oninput="setText('${item.id}',this.value)">${esc(val)}</textarea>`;
    } else {
        body = `<p class="inline-note">Question type not yet configured.</p>`;
    }
 
    return `
    <p class="question-text">${esc(item.text || 'This question has not yet been defined')}</p>
    ${body}`;
}
 
function renderSummary() {
    return `
    <div class="summary-wrap">
      <h2 class="summary-title">Survey Complete</h2>
    </div>`;
}
 
function render() {
    const app = document.getElementById('app');
    const isSummary = cur >= pages.length;
    const bnav = document.getElementById('bottom-nav');
 
    updateFooter();
 
    if (isSummary) {
        bnav.style.display = 'none';
        app.innerHTML = renderSummary();
        return;
    }
 
    bnav.style.display = 'flex';
    const page = pages[cur];
 
    document.getElementById('btn-back').disabled = (cur === 0);
    document.getElementById('btn-next').textContent = (cur === pages.length - 1) ? 'Finish' : 'Next';
    document.getElementById('nav-pager').textContent = `Question ${pages.findIndex(p => p.item.id === page.item.id) + 1} of ${pages.length}`;
 
    app.innerHTML = renderQuestionPage(page);
}

function go(dir) {
    cur = Math.max(0, Math.min(pages.length, cur + dir));
    render();
    window.scrollTo({ top: 0});
}

function restart() {
    responses = {};
    cur = 0;
    render();
    window.scrollTo({ top: 0 });
}

function loadQuiz() {
    pages = buildPages(quiz);
    responses = {};
    cur = 0;
    render();
}
 
function selectMC(qId, optId) {
    responses[qId] = optId;
    render();
}

function setText(qId, val) {
    responses[qId] = val;
    updateFooter();
}

function esc(s) {
    return String(s)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

loadQuiz(quiz);