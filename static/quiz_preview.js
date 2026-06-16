let pages = [];
let cur = 0;
let responses = {};
let history = [];

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
    const traveled = history.length;

    if (cur >= pages.length) {
        document.getElementById('footer-fill').style.width = '100%';
        document.getElementById('footer-label').textContent = `${traveled} question(s) answered`;
        document.getElementById('footer-remain').textContent = 'All done!';
        return;
    }
    console.log(isPathDeterminate(cur));
    if (isPathDeterminate(cur)) {
        const answered = Object.values(responses).filter(v => v !== '' && v !== null && v !== undefined).length;
        const percent = total ? Math.round((answered / total) * 100) : 0;
        const remaining = total - answered;
        document.getElementById('footer-fill').style.width = percent + '%';
        document.getElementById('footer-label').textContent = `${answered} of ${total} question(s) answered`;
        document.getElementById('footer-remain').textContent = remaining > 0 ? `${remaining} remaining` : 'All done!';
    } else {
        const percent = Math.round((traveled / (traveled + 1)) * 100);
        document.getElementById('footer-fill').style.width = percent + '%';
        document.getElementById('footer-label').textContent = `${traveled} question(s) answered`;
        document.getElementById('footer-remain').textContent = '';
    }
}

// check if the path ahead of an index has branching or is linear.
function isPathDeterminate(startIdx) {
    let idx = startIdx;
    const visited = new Set();
    while (idx >= 0 && idx < pages.length) {
        if (visited.has(idx)) return false;
        visited.add(idx);
        const answers = pages[idx].item.answer || [];
        const destinations = [];
        for (const a of answers) {
            const dest = resolveLeadsTo(a.leads_to);
            if (!destinations.includes(dest)) destinations.push(dest);
        }
        if (destinations.length > 1) return false;
        if (destinations.length === 0) { idx++; continue; }
        const next = destinations[0];
        if (next >= pages.length) break;
        idx = next;
    }
    return true;
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
    } else if (item.type === 'result') {
        body = `
        <div class="result-display">
            ${item.result_body ? `<p class="result-body">${esc(item.result_body)}</p>` : ''}
        </div>`;
    } else {
        body = `<p class="inline-note">Question type not yet configured.</p>`;
    }
    return `
    <p class="question-text">${esc(item.text) || 'This question has not yet been defined'}</p>
    ${body}`;
}

/* ----------------- TEST CODE ----------------- */

function getQuestionsAndAnswer(){
    textAnswersAndQuestions = [];
    count = 0;
    const responseEntries = Object.entries(responses);

    while(count != responseEntries.length){

        answeredQuestionID = responseEntries[count][0];
        selectedAnswerID = responseEntries[count][1];

        page = pages[count]

        singleResponseText = [];
        if(page.item.id === answeredQuestionID){
            singleResponseText.push(page.item.text);
        } else {
            singleResponseText.push("NO QUESTION");
        }

        specificAnswer = page.item.answer.find(ans => ans.id === selectedAnswerID);

        if(specificAnswer){
            singleResponseText.push(specificAnswer.text);
        } else if (page.item.type === 'text'){
            singleResponseText.push(selectedAnswerID);
        } else {
            singleResponseText.push("NO ANSWER WAS GIVEN");
        }
        textAnswersAndQuestions.push(singleResponseText);
        count++;
    }
    return textAnswersAndQuestions;   
}

/* ----------------- TEST CODE END ----------------- */



/**
 * Called at the end of the survey to indicate that it's done
 * @returns the page at the end of the survey
 */
function renderSummary() {
    listOfQuestionAndAnswers = getQuestionsAndAnswer()
    return `
    <div class="summary-wrap">
      <h2 class="summary-title">${JSON.stringify(responses)}</h2>
    </div>
    <div class="summary-wrap">
      <h2 class="summary-title">${JSON.stringify(listOfQuestionAndAnswers)}</h2>
    </div>`;
}

/**
 * Render the page each time it is needed to render
 * @returns is here in order to escape after a certain condition
 */
let renderDepth = 0;
function render() {
    renderDepth++;
    if (renderDepth > 50) { console.error('RENDER RECURSION'); renderDepth--; return; }
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

    document.getElementById('btn-back').disabled = (history.length === 0);
    document.getElementById('btn-back').onclick = () => goBack();

    document.getElementById('btn-next').textContent = (cur === pages.length - 1) ? 'Finish' : 'Next';
    document.getElementById('btn-next').onclick = () => nextQuestion(pages[cur].item.id);
    document.getElementById('btn-next').disabled = !isCurrentAnswered();


    app.innerHTML = renderQuestionPage(page);
    renderDepth--;
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

function resolveLeadsTo(leads_to) {
    if (!leads_to) {
        return pages.length;
    }
    const index = pages.findIndex(p => p.item.id == leads_to);
    return index !== -1 ? index : pages.length;
}

function nextQuestion(qId) {
    const item = pages[cur].item;
    const allAnswers = quiz.categories.flatMap(cat => cat.items).flatMap(i => i.answer);

    const answerId = responses[qId];
    const answer = allAnswers.find(a => a.id === answerId) || item.answer?.[0];
    const leads_to = answer?.leads_to;

    history.push(cur);
    cur = resolveLeadsTo(leads_to);
    render();
    window.scrollTo({ top: 0 });
}

function goBack() {
    if (history.length === 0) return;
    cur = history.pop();
    render();
    window.scrollTo({ top: 0 });
}

/**
 * Restart the quiz after the quiz has been finished
 */
function restart() {
    responses = {};
    cur = 0;
    history = [];
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
    document.getElementById('btn-next').disabled = !isCurrentAnswered();
}

function isCurrentAnswered() {
    const item = pages[cur]?.item;
    if (!item) return true;

    if (item.type == 'mc' || item.type == 'sldr') {
        return responses[item.id] != undefined && responses[item.id] != null && responses[item.id] != '';
    }
    if (item.type == 'text') {
        return (responses[item.id] || '').trim() != '';
    }
    // fallback for things without answers like result!
    return true;
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