//instance variable.
let pages = [];
let cur = 0;
let responses = {};
let history = [];
let CURRENT_USER_ID = null;

// Ordered, de-duplicated list of every question id the user has actually landed on while
// taking the quiz (unlike `history`, this is never popped -- it's a permanent travel log).
// Used at the end of the quiz to know which "append to email" text to include.
let visitedNodeIds = [];

/**
 * Record that the user has landed on a given page, if it hasn't already been recorded.
 * @param {*} idx the pages[] index the user just landed on
 */
function recordVisit(idx) {
    const item = pages[idx]?.item;
    if (!item) return;
    if (!visitedNodeIds.includes(item.id)) {
        visitedNodeIds.push(item.id);
    }
}

/**
 * @param {*} quiz the quiz that is being previewed 
 * @returns a list containing every question
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
 * @returns when the quiz is fully finished, as a way to escape and not continue with unneded behavior 
 */
function updateFooter() {
    const answered = history.filter(idx => pages[idx].item.type !== 'result').length;
    if (cur >= pages.length) {
        document.getElementById('footer-fill').style.width = '100%';
        document.getElementById('footer-label').textContent = `${answered} questions answered`;
        document.getElementById('footer-remain').textContent = '';
        return;
    }


    const [min, max] = getRemainingRange(cur);


    const worstTotal = answered + max;
    const bestTotal = answered + min;

    const worstPct = worstTotal > 0 ? Math.round((answered / worstTotal) * 100) : 0;
    const bestPct = bestTotal > 0 ? Math.round((answered / bestTotal) * 100) : 0;

    // progress bar just goesd off worst case scenario for the time being. maybe we could add a range later? not sure best way to do this.
    document.getElementById('footer-fill').style.width = bestPct + '%';


    document.getElementById('footer-label').textContent = (worstPct == bestPct)
        ? `${worstPct}% complete`
        : `${worstPct}–${bestPct}% complete`;


    document.getElementById('footer-remain').textContent = (min == max)
        ? `${max} remaining`
        : `${min}–${max} remaining`;
}


/**
 * gets the number of remaining questions given a start index
 * @param {*} startIdx the start index that we are using 
 * @returns the range of question left to answer
 */
function getRemainingRange(startIdx) {
    const memo = new Map();
    const visiting = new Set();

    function crawl(idx) {
        if (idx >= pages.length) return [0, 0];
        if (visiting.has(idx)) return [0, 0];
        if (memo.has(idx)) return memo.get(idx);

        visiting.add(idx);

        const item = pages[idx].item;
        const answers = item.answer || [];
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

        // "result" pages aren't real inputs, so they shouldn't count toward remaining
        const weight = item.type === 'result' ? 0 : 1;

        const result = [
            weight + Math.min(...childRanges.map(r => r[0])),
            weight + Math.max(...childRanges.map(r => r[1]))
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
    } else if (item.type === 'drag') {

        // Return the container markup directly in the body string
        body = `
            <div class="drag-drop-container" id="drag-drop-container-${item.id}">
                <div class="drop-zones-area"></div>
                <div class="drag-items-area"></div>
            </div>
        `;

        // Wait a split second for the DOM string to render, then populate items & attach drag listeners
        setTimeout(() => {
            addAllDropsAndDrags(item);
        }, 0);
    } else {
        body = `<p class="inline-note">Question type not yet configured.</p>`;
    }
    return `
    <p class="question-text">${esc(item.text) || 'This question has not yet been defined'}</p>
    ${body}`;
}

/**
 * Extract the current location of the drag and drop boxes and puts them is string format for storage in database
 * @param {*} dropArea <div> that holds the drop boxes on the page
 * @returns JSON formatted list of the current order of the drags and drops
 */
function extractDragDropState(dropArea) {
    const dropBoxes = dropArea.querySelectorAll('.target-box');

    let allIdsArray = [];
    let allTextsArray = [];

    for (const dropBox of dropBoxes) {
        // Find all drag boxes currently dropped inside THIS specific drop box
        const nestedDrags = dropBox.querySelectorAll('.drag-box');

        let dragDropIDString = dropBox.id;

        // Get just the drop box's title (ignoring nested drag elements)
        let dropBoxTitle = "";
        const titleSpan = dropBox.querySelector('span');
        if (titleSpan) {
            dropBoxTitle = titleSpan.textContent;
        } else {
            dropBoxTitle = Array.from(dropBox.childNodes)
                .filter(node => node.nodeType === Node.TEXT_NODE)
                .map(node => node.textContent.trim())
                .join('');
        }

        let dragDropTextString = dropBoxTitle;

        for (const drag of nestedDrags) {
            dragDropIDString += "|" + drag.id;
            dragDropTextString += "|" + drag.textContent;
        }

        // Push this box's pipe-separated string into our main arrays
        allIdsArray.push(dragDropIDString);
        allTextsArray.push(dragDropTextString);
    }

    // Return a single object with combined, comma-separated strings
    return {
        dragDropId: allIdsArray.join(', '),
        dragDropText: allTextsArray.join(', ')
    };
}

/**
 * Populates and updates the question page for the drag style question.
 * @param {*} item The current question that is being answered on the quiz: item = page.item
 * @returns Will only return if there is an error
 */
function addAllDropsAndDrags(item) {
    // Locate the container 
    const container = document.getElementById(`drag-drop-container-${item.id}`);

    if (!container) {
        console.error(`Container #drag-drop-container-${item.id} not found in DOM.`);
        return;
    }

    const dropArea = container.querySelector('.drop-zones-area');
    const dragArea = container.querySelector('.drag-items-area');

    // Clear any existing content
    dropArea.innerHTML = '';
    dragArea.innerHTML = '';

    // Extract drags and drops from item.answer array
    let dragsList = [];
    let dropsList = [];

    if (Array.isArray(item.answer)) {
        item.answer.forEach(entry => {
            if (entry.drags) dragsList = entry.drags;
            if (entry.drops) dropsList = entry.drops;
        });
    }

    // Render Drop Target Boxes
    dropsList.forEach((drop, index) => {
        const dropElem = document.createElement('div');
        dropElem.id = drop.id || `drop-${item.id}-${index}`;
        dropElem.className = 'box target-box';
        dropElem.innerHTML = `<span>${drop.text || 'Drop Zone'}</span>`;

        // drag & drop event handling
        dropElem.addEventListener('dragover', (e) => {
            e.preventDefault(); // Essential to allow drop
            dropElem.classList.add('drag-over');
        });

        dropElem.addEventListener('dragleave', () => {
            dropElem.classList.remove('drag-over');
        });

        dropElem.addEventListener('drop', (e) => {
            e.preventDefault();
            dropElem.classList.remove('drag-over');

            const draggedId = e.dataTransfer.getData('text/plain');
            const draggedElem = document.getElementById(draggedId);

            if (draggedElem) {
                // Append the dragged box into the drop zone
                dropElem.appendChild(draggedElem);
                /** 
                 * This will save the users response for JSON and 
                 * if they want to go back and look at there answer during the quiz
                 * */
                const questionResults = extractDragDropState(dropArea)
                responses[item.id] = {
                    dragDropId: questionResults.dragDropId,
                    dragDropText: questionResults.dragDropText
                };
            }
        });

        dropArea.appendChild(dropElem);
    });


    // Render Draggable Boxes
    dragsList.forEach((drag, index) => {
        const dragElem = document.createElement('div');
        dragElem.id = drag.id || `drag-${item.id}-${index}`;
        dragElem.className = 'box drag-box';
        dragElem.setAttribute('draggable', 'true');
        dragElem.textContent = drag.text || 'Drag Me';

        dragElem.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', dragElem.id);
        });

        dragArea.appendChild(dragElem);

    });
    selectDRAG(responses[item.id]);
}

/**
 * Keeps the users response to the question saved for when the 
 * data is formatted to be accepted into the data base
 * @param {*} savedResponse The users response to the question
 */
function selectDRAG(savedResponse) {
    if (savedResponse && savedResponse.dragDropId) {
        // savedResponse.dragDropId looks like: "dropId|dragId1|dragId2, dropId2|dragId3"
        const dropBoxGroups = savedResponse.dragDropId.split(', ');

        for (const group of dropBoxGroups) {
            const ids = group.split('|');
            const dropBoxId = ids[0];
            const dropBoxElem = document.getElementById(dropBoxId);

            if (dropBoxElem) {
                // Loop through all drag items belonging to this drop box
                for (let i = 1; i < ids.length; i++) {
                    const dragId = ids[i];
                    const dragElem = document.getElementById(dragId);

                    if (dragElem) {
                        // Move the drag box back into its saved drop zone
                        dropBoxElem.appendChild(dragElem);
                    }
                }
            }
        }
    }
}

/**
 * Gets the userID from the current session which will be stored along with the users completed quiz data 
 */
async function getUserID() {
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
function formatCompletedQuizData() {

    const responseEntries = Object.entries(responses); // <--- [[questionId, optionID],[index 0, index 1]]

    const questionIdIndex = 0;
    const optionIdIndex = 1;
    const textResponseIndex = 1;


    //Grabs the title and id of the quiz being taken and makes catagories array
    const usersQuizResponseData = {
        userID: CURRENT_USER_ID,
        quizID: quiz.id,
        timeStamp: new Date().toUTCString(),
        quizCategories: []
    };

    // Loop though all category types and load id of each 
    // Load question ids 
    // Load answer text and id the user selected
    for (const cat of quiz.categories) {

        // Load current category name and ID
        const category = {
            id: cat.id,
            questions: []
        };
        // Load Questions into the category
        for (const ques of cat.items) {
            const question = {
                id: ques.id,
                //type: ques.type,
                UserAnswer: []
            };

            // Special case for 'text' questions since there not stored normally
            if (ques.type === 'text') {
                let userAnswer = null;
                // Compare user response id to the answer id's
                for (const response of responseEntries) {
                    if (ques.id === response[questionIdIndex]) {
                        userAnswer = {
                            text: response[textResponseIndex],
                            id: Math.random().toString(36).slice(2, 9)
                        };
                        break;
                    }
                }
                if (userAnswer) {
                    question.UserAnswer.push(userAnswer);
                }
            }
            //  Special case for 'drag' questions since there not stored normally
            if (ques.type === 'drag') {
                let userAnswer = null;
                // Compare user response id to the answer id's
                for (const response of responseEntries) {

                    if (ques.id === response[questionIdIndex]) {
                        userAnswer = {
                            text: response[textResponseIndex].dragDropText,
                            id: response[textResponseIndex].dragDropId
                        };
                        break;
                    }
                }
                if (userAnswer) {
                    question.UserAnswer.push(userAnswer);
                }
            }

            // compare user response to the responseEntries optionID's for 'mc' and 'sldr'
            for (const ans of ques.answer) {
                let userAnswer = null;
                // Compare user response id to the answer id's
                for (const response of responseEntries) {

                    if (ans.id === response[optionIdIndex]) {
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

// Sends out POST with users quiz data for the database to process
async function postUserData(usersQuizResponseData) {
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

/**
 * Look through every node the user actually traveled to during the quiz and pull out
 * the ones that have "append to email" checked, in the order they were visited.
 * @returns an array of question items (from quiz.categories) that have email-append set
 */
function getVisitedEmailAppendItems() {
    const allQuestions = quiz.categories.flatMap(cat => cat.items);
    return visitedNodeIds
        .map(id => allQuestions.find(q => q.id === id))
        .filter(item => item && item['email-append']);
}

/**
 * Join together the "email-append-text" of every visited node that has email-append checked,
 * one after the other, in the order the user traveled through them.
 * @returns the combined email body text
 */
function buildEmailFollowupBody() {
    return getVisitedEmailAppendItems()
        .map(item => (item['email-append-text'] || '').trim())
        .filter(text => text !== '')
        .join('\n\n');
}

/**
 * Show the email input + submit button in place of the "send me an email" button.
 */
function showEmailFollowupInput() {
    const container = document.getElementById('email-followup');
    if (!container) return;
    container.innerHTML = `
        <div id="email-followup-steps">
            <input type="email" id="email-followup-address" placeholder="hello@gmail.com"/>
            <button class="email-prompt" onclick="submitEmailFollowup()">
                Send
            </button>
        </div>
        <p id="email-followup-status"></p>
    `;
    const input = document.getElementById('email-followup-address');
    if (input) input.focus();
}

/**
 * Validate the entered email, then POST it (along with the combined email-append text
 * for every visited node) to the backend so it can be sent via flask-mailing.
 */
async function submitEmailFollowup() {
    const input = document.getElementById('email-followup-address');
    const status = document.getElementById('email-followup-status');
    const submitBtn = document.getElementById('email-followup-submit');
    const email = (input?.value || '').trim();

    // very light client-side sanity check; the backend should still validate this
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        if (status) status.textContent = `'${email}' is not a valid address.`;
        return;
    }

    const body = buildEmailFollowupBody();

    if (submitBtn) submitBtn.disabled = true;
    if (input) input.disabled = true;

    try {
        const response = await fetch('/send-quiz-email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                userID: CURRENT_USER_ID,
                quizID: quiz.id,
                email,
                body
            })
        });

        if (!response.ok) {
            throw new Error('HTTP error');
        }

        const container = document.getElementById('email-followup');
        if (container) {
            container.innerHTML = `<p> Email sent.
            <br/>
            ${body}</p>`;
        }
    } catch (error) {
        console.error(error);
        if (status) status.textContent = error;
        if (submitBtn) submitBtn.disabled = false;
        if (input) input.disabled = false;
    }
}

/**
 * Called at the end of the survey to indicate that it's done
 * @returns the page at the end of the survey
 */
function renderSummary() {

    testData = formatCompletedQuizData();
    postUserData(testData);

    const hasEmailAppendContent = getVisitedEmailAppendItems().length > 0;

    return `
    <div class="summary-wrap">
        <h2 class="summary-title">Quiz Complete!</h2>
       <div>
           <div>
                <h3>JSON Preview:</h3>
                <pre>
                  <code>${JSON.stringify(testData, null, 1)}</code>
                </pre>
           </div>
            ${hasEmailAppendContent ? `
            <div id="email-followup">
                <button class="email-prompt" onclick="showEmailFollowupInput()">
                    Send me an email with next steps
                </button>
            </div>
       </div>
        ` : ''}
    </div>
    `;
}

/**
 * Check if a page is the last page, used to check whether the next button text need to be changed to "Finish" instead
 * @returns if this page is the last page or not
 */
function isLastPage() {
    const item = pages[cur]?.item;
    if (!item)
        return true;

    if (item.type === 'result' || item.type === 'text') {
        const leads_to = item.answer?.[0]?.leads_to;
        if (!leads_to)
            return true;
        return resolveLeadsTo(leads_to) >= pages.length;
    }

    const answerId = responses[item.id];
    if (!answerId) {
        return cur === pages.length - 1;
    }

    const answer = item.answer?.find(a => a.id === answerId);
    if (!answer)
        return false;

    const leads_to = answer.leads_to;
    if (!leads_to) {
        return cur === pages.length - 1;
    }

    return resolveLeadsTo(leads_to) >= pages.length;
}

/**
 * Render the page each time it is needed to render
 * @returns is here in order to escape if the current page is the Summary page, or if the renderDepth is too big (and is likely a recursion case)
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

    document.getElementById('btn-next').textContent = (isLastPage()) ? 'Finish' : 'Next';
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

/**
 * Resolve a leads_to value to an index in the pages array.
 * @param {*} leads_to the question id to resolve, or null/undefined
 * @returns the index of the target page in pages[], or pages.length if not found/null
 */
function resolveLeadsTo(leads_to) {
    if (!leads_to) {
        return pages.length;
    }
    const index = pages.findIndex(p => p.item.id == leads_to);
    return index !== -1 ? index : pages.length;
}


/**
 * Advance the quiz to the next question based on the current question's leads_to value.
 * @param {*} qId the id of the current question being answered
 */

function nextQuestion(qId) {
    const item = pages[cur].item;

    if (item.type === 'drag') {
        history.push(cur);
        cur++; // Just go to the next chronological page normally
    } else {
        const allAnswers = quiz.categories.flatMap(cat => cat.items).flatMap(i => i.answer);
        const answerId = responses[qId];
        const answer = allAnswers.find(a => a.id === answerId) || item.answer?.[0];
        const leads_to = answer?.leads_to;

        history.push(cur);
        cur = resolveLeadsTo(leads_to);
        recordVisit(cur);
    }

    render();
    window.scrollTo({ top: 0 });
}

/**
 * Go back to a previous question
 * @returns if there is no way to go back has it's the first question
 */
function goBack() {
    if (history.length === 0) return;
    cur = history.pop();
    render();
    window.scrollTo({ top: 0 });
}

/**
 * Restart the quiz after the quiz has been finished, if the user whishes it.
 */
function restart() {
    responses = {};
    cur = 0;
    history = [];
    visitedNodeIds = [];
    recordVisit(cur);
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
    visitedNodeIds = [];
    recordVisit(cur);
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
 * choose an answer to a slider question
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

/**
 * Check whether the current page has been answered sufficiently to allow further movement.
 * @returns true if the current page can be advanced past, false otherwise
 */
function isCurrentAnswered() {
    const item = pages[cur]?.item;
    if (!item) return true;

    // TODO: Eventually add drag parameters
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

//the following function will be called once every time we call this file.
getUserID();
loadQuiz(quiz);