let pages = [];
let cur = 0;
let responses = {};

/**
 * @param {*} quiz the quiz that is being previewed 
 * @returns a list containing every question (even null question --> do we want to remove that part?)
 */
function buildPages(quiz) {
    const list = [];
    for (const category of quiz.categories) {
        for (const item of category.items) {
            list.push({ type: 'question', item });
        }
    }
    return list;
}


/**
 * Update the footer each time a question is answered, is reponsible for the bar filling at the bottom 
 * Allow the user to have a sense of how many question there are instead of trudging onward without any idea of what is awaiting them
 */
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


/**
 * render a question on the page
 * @param {*} page the specific question that is being displayed
 * @returns the html page containing the question
 */

function renderQuestionPage(page) {
    const item = page.item;
    let body = '';

    if (item.type === 'mc') {
        const options = item.answer;
        if (!options.length) {
            body = `<p class="inline-note">No answer options have been defined yet.</p>`;
        } else {
            body = 
                `<div class="options-list">` +
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
    } else if (item.type === 'sldr') {
        const options = item.answer;
        if (!options.length) {
            body = `<p class="inline-note">No answer options have been defined yet.</p>`;
            labels = `<p class="inline-note">No answer labels have been defined yet.</p>`;
        } else {
            const currentResponseId = responses[item.id];
            const currentIndex = options.findIndex(opt => opt.id === currentResponseId);
            const sliderValue = currentIndex !== -1 ? currentIndex : 0;

            body = 
            `<div class="slider-container">
                <input
                    type="range"
                    min="0"
                    max="${options.length - 1}"
                    step="1"
                    value="${sliderValue}"
                    id="notchedSlider"
                    class="slider"
                    onchange="selectSLDR('${item.id}', this.value, ${esc(JSON.stringify(options))})"
                >
                <div class="slider-notches">
                    ${'<span></span>'.repeat(options.length)}
                </div>
            </div>`+
            `<div class="slider-labels" style="--count:${options.length}">
                ${options.map((option, i) => {
                    const label = option.text || `Option ${String.fromCharCode(65 + i)}`;
                    const sel = currentResponseId ? currentResponseId == option.id : i === 0;
                    return `
                    <span class="${sel ? 'slider-label-selected' : 'slider-label'}" 
                        style="left: ${i * 100 / (options.length - 1)}%">
                        ${esc(label)}
                    </span>
                    `;
                }).join('')}
            </div>`
        }
    } else {
        body = `<p class="inline-note">Question type not yet configured.</p>`;
    }
    return `
    <p class="question-text">${esc(item.text) || 'This question has not yet been defined'}</p>
    ${body}`;
}

/**
 * Called at the end of the survey to indicate that it's done
 * @returns the page at the end of the survey
 */
function renderSummary() {
    return `
    <div class="summary-wrap">
      <h2 class="summary-title">Survey Complete</h2>
    </div>`;
}

/**
 * Render the page each time it is needed to render
 * @returns is here in order to escape after a certain condition
 */
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

/**
 * Go to a question before or after the current one
 * @param {*} dir the direction that you need to go in(back is -1 forward is 1) 
 */

function go(dir) {
    cur = Math.max(0, Math.min(pages.length, cur + dir));
    render();
    window.scrollTo({ top: 0 });
}



/**
 * Restart the quiz after the quiz has been finished
 */
function restart() {
    responses = {};
    cur = 0;
    render();
    window.scrollTo({ top: 0 });
}


/**
 * Load a quiz. Is called once when the page is first created
 */
function loadQuiz() {
    pages = buildPages(quiz);
    responses = {};
    cur = 0;
    render();
}

/**
 * Choose the answer to a multiple choice question
 * @param {*} qId the question
 * @param {*} optId the option to the quiz
 */
function selectMC(qId, optId) {
    responses[qId] = optId;
    render();
}

/**
 * 
 * @param {*} qId the question
 * @param {*} sliderValue current slider value
 * @param {*} optionsArray array of all possible answers to the question
 */
function selectSLDR(qId, sliderValue, optionsArray) {
    const selectedOption = optionsArray[sliderValue];
    responses[qId] = selectedOption.id;
    render();
}

/**
 * Choose the answer to a text based question
 * @param {*} qId the question 
 * @param {*} val the answer to the quiz 
 */
function setText(qId, val) {
    responses[qId] = val;
    updateFooter();
}

/**
 * Since html is a slighly annoying language, user input can easily break it. This is here to sanitize an input
 * @param {*} s the text that need escaping from  
 * @returns the string sanitized
 */
function esc(s) {
    return String(s)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
//will be called once every time we call this file.
loadQuiz(quiz);