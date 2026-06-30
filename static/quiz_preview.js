let pages = [];
let cur = 0;
let responses = {};
let history = [];
let CURRENT_USER_ID = null;

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
 * Update the footer each time a question is answered, is responsible for the bar filling at the bottom 
 * Allow the user to have a sense of how many question there are instead of trudging onward without any idea of what is awaiting them
 */
function updateFooter() {
    const answered = history.length;
    if (cur >= pages.length) {
        document.getElementById('footer-fill').style.width = '100%';
        document.getElementById('footer-label').textContent = `${answered} questions answered`;
        document.getElementById('footer-remain').textContent = 'All done!';
        return;
    }

    
    const [min, max] = getRemainingRange(cur);

    
    const worstTotal = answered + max;
    const bestTotal  = answered + min;  

    const worstPct = worstTotal > 0 ? Math.round((answered / worstTotal) * 100) : 0;
    const bestPct  = bestTotal  > 0 ? Math.round((answered / bestTotal)  * 100) : 0;

    // progress bar just goesd off worst case scenario for the time being. maybe we could add a range later? not sure best way to do this.
    document.getElementById('footer-fill').style.width = worstPct + '%';

    
    document.getElementById('footer-label').textContent = (worstPct == bestPct)
        ? `${worstPct}% complete`
        : `${worstPct}–${bestPct}% complete`;


    document.getElementById('footer-remain').textContent = (min == max)
        ? `${max} remaining`
        : `${min}–${max} remaining`;
}

// gets the number of remaining questions given a start index
function getRemainingRange(startIdx) {
    const memo = new Map();
    const visiting = new Set();

    function crawl(idx) {
        if (idx >= pages.length) return [0, 0];  
        if (visiting.has(idx)) return [0, 0];
        if (memo.has(idx)) return memo.get(idx);

        visiting.add(idx);

        const answers = pages[idx].item.answer || [];
        let childRanges;

        // if theres no answers, just add 1
        if (answers.length == 0) {
            childRanges = [crawl(idx + 1)];
        } else {
            // remove duplicate destinations
            const dests = [...new Set(answers.map(a => resolveLeadsTo(a.leads_to)))];
            childRanges = dests.map(dest => crawl(dest));
        }

        visiting.delete(idx);

        const result = [
            1 + Math.min(...childRanges.map(r => r[0])),
            1 + Math.max(...childRanges.map(r => r[1]))
        ];

        memo.set(idx, result);
        return result;
    }

    return crawl(startIdx);
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

/**
 * Gets the userID from the current session which will be stored along with the users completed quiz data 
 */
async function getUserID(){
    try {
        const response = await fetch('/get-user-id');
        const data = await response.json();
        
        CURRENT_USER_ID = data.userId; 
        console.log("User ID set to:", CURRENT_USER_ID);
    } catch (error) {
        CURRENT_USER_ID = 'NO User ID Found'; 
        console.error("Error getting user ID:", error);
    }
}

/**
 * Takes in completed quiz and collects and formats the answers the user gave to correspond the the question and category.
 * @returns usersQuizResponseData this is the users answers to the questions in JSON format.
 */
function formatCompletedQuizData(){

    // TODO: Have it store the UserID of the person taking the quiz
    const responseEntries = Object.entries(responses); // <--- [[questionId, optionID],[index 0, index 1]]
    const questionIdIndex = 0;
    const optionIdIndex = 1;
    const textResponseIndex = 1;
    

    //Grabs the title and id of the quiz being taken and makes catagories array
    const usersQuizResponseData = {
        userID: CURRENT_USER_ID, // <--- Temporary id
        quizID: quiz.id,
        timeStamp: new Date().toUTCString(),
        quizCategories: []
    };

    // Loop though all category types and load id of each 
        // Load question ids 
            // Load answer text and id the user selected
    for (const cat of quiz.categories){

        // Load current category name and ID
        const category = {
            id: cat.id,
            questions: [] 
        };
        // Load Questions into the category
        for (const ques of cat.items){
            const question = {
                id: ques.id,
                //type: ques.type,
                UserAnswer: []
            };

            // Special case for 'text' questions since there not stored normally
            if(ques.type === 'text'){
                let userAnswer = null;
                // Compare user response id to the answer id's
                for(const response of responseEntries){
                    if(ques.id === response[questionIdIndex]){
                        userAnswer = {
                            text: response[textResponseIndex],
                            id: Math.random().toString(36).slice(2, 9) //TEST
                        };
                        break;
                    }
                }
                if (userAnswer) {
                    question.UserAnswer.push(userAnswer);
                } 
            }
            // compare user response to the responseEntries optionID's for 'mc' and 'sldr'
            for (const ans of ques.answer){
                let userAnswer = null;
                // Compare user response id to the answer id's
                for(const response of responseEntries){

                    if(ans.id === response[optionIdIndex]){
                        userAnswer = {
                            text: ans.text,
                            id: ans.id
                        };
                    }
                }
                if (userAnswer) {
                    question.UserAnswer.push(userAnswer);
                } 
            }
            category.questions.push(question);
        }
        usersQuizResponseData.quizCategories.push(category);
    }
    return usersQuizResponseData;
}

//-----------------TEST---FUNCTION-----------------////-----------------TEST---FUNCTION-----------------////-----------------TEST---FUNCTION-----------------//
//-----------------TEST---FUNCTION-----------------////-----------------TEST---FUNCTION-----------------////-----------------TEST---FUNCTION-----------------//
//-----------------TEST---FUNCTION-----------------////-----------------TEST---FUNCTION-----------------////-----------------TEST---FUNCTION-----------------//
async function postUserData(usersQuizResponseData){
    data = usersQuizResponseData;

    try {
        const response = await fetch('/quiz-data', {
          method: 'POST', 
          headers: {
            'Content-Type': 'application/json' 
          },
          body: JSON.stringify(data) 
        });
    
        if (!response.ok) {
          throw new Error(`HTTP error!`);
        }
    
        const result = await response.json();
        console.log('Success:', result);

    } catch (error) {
        console.error('Error during POST request:', error);
    }
}
//-----------------TEST---FUNCTION-----------------////-----------------TEST---FUNCTION-----------------////-----------------TEST---FUNCTION-----------------//
//-----------------TEST---FUNCTION-----------------////-----------------TEST---FUNCTION-----------------////-----------------TEST---FUNCTION-----------------//
//-----------------TEST---FUNCTION-----------------////-----------------TEST---FUNCTION-----------------////-----------------TEST---FUNCTION-----------------//


/**
 * Called at the end of the survey to indicate that it's done
 * @returns the page at the end of the survey
 */
function renderSummary() {
    
    testData = formatCompletedQuizData();
    postUserData(testData);
    return `
    <div class="summary-wrap">
        <h2 class="summary-title">Quiz Results JSON Preview</h2>
        <pre style="margin-top: 400px; background: #272822; color: #f8f8f2; padding: 15px; border-radius: 5px; text-align: left; overflow-x: auto;">
          <code>${JSON.stringify(testData, null, 1)}</code>
        </pre>
    </div>
    `; 
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
 * Since html is a slightly annoying language, user input can easily break it. This is here to sanitize an input
 * @param {*} s the text that need escaping from  
 * @returns the string sanitized
 */
function esc(s) {
    return String(s)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}
//will be called once every time we call this file.
getUserID();
loadQuiz(quiz);
