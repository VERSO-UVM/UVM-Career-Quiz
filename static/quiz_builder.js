// class variable, alongside quiz (a dictionary), which is defined in quiz_builder.html
let active_category_Id = null;
let active_question_Id = null;
isDirty = false;
const _role = (typeof USER_ROLE !== 'undefined') ? USER_ROLE : 'reader';

/**
 * helper function, create a random string to id the div
 */
function uid() {
    return Math.random().toString(36).slice(2, 9);
}

function markDirty() { 
    isDirty = true; 
}
function markClean() { 
    isDirty = false; 
}

/**
 * get the quiz information from the two element named in the same way
 */
function getQuizInfo() {
    quiz.title = document.getElementById('quiz-title').value;
    quiz.desc = document.getElementById('quiz-desc').value;
}


/**
 * Used in conjunction with a button in the html, create a category upon which you can add question. The category is added to the quiz dict\
 * @returns the return is here as a way to break out of the function
 */
function addCategory() {
    const id = uid();
    //25 is an arbitrary number for the sake of having a limit, might want to remove that one day
    if (quiz.categories.length >= 25) {
        alert("Too many categories");
        return;
    }
    quiz.categories.push({ id, name: 'Category ' + (quiz.categories.length + 1), items: [] });
    render();
    markDirty()
}

/**
 * Change the name of a category
 * @param {*} id the id of the category, allow us to find it in the dict
 * @param {*} new_name the new name for the category 
 */
function changeCategoryName(id, new_name) {
    const category = quiz.categories.find(category => category.id === id);
    if (category) {
        category.name = new_name;
        if (active_category_Id === id) {
            document.getElementById('editor_category_title').textContent = new_name;
        }
    }
    markDirty()
}
/**
 * Remove a specific category (and it's eventual childs) from the dict
 * @param {*} id the id of the category, allow us to find it in the dict
 */
function removeCategory(id) {
    quiz.categories = quiz.categories.filter(category => category.id !== id);

    // Renumber categorys that still have default names
    quiz.categories.forEach((category, index) => {
        if (/^category \d+$/.test(category.name)) {
            category.name = 'Category ' + (index + 1);
        }
    });

    // If the removed category was active, close the editor
    if (active_category_Id === id) {
        active_category_Id = null;
        closeEditor();
    }
    markDirty()
    render();
}


/**
 * Open the editor in the middle of the screen, allow user to add question to the category
 * @param {*} id 
 * @returns here to break out of the function in case of unexpected behavior 
 */
function openEditor(id) {
    active_category_Id = id;
    active_question_Id = null;
    const category = quiz.categories.find(b => b.id === id);
    if (!category)
        return;

    document.getElementById('question_editor').style.display = 'flex';
    document.getElementById('empty_state').style.display = 'none';
    document.getElementById('editor_category_title').textContent = category.name;

    renderQuestions(id);
    closeAnswerPanel();

    // Highlight active category in sidebar
    document.querySelectorAll('.category_item').forEach(el => el.classList.remove('active'));
    const activeEl = document.querySelector(`.category_item[data-id="${id}"]`);
    if (activeEl)
        activeEl.classList.add('active');
}


/**
 * Allow for a clean way to close the editor in the middle. 
 */
function closeEditor() {
    document.getElementById('question_editor').style.display = 'none';
    document.getElementById('empty_state').style.display = 'flex';
    document.querySelectorAll('.category_item').forEach(el => el.classList.remove('active'));
    active_category_Id = null;
    active_question_Id = null;
    closeAnswerPanel();
}

/**
 * Add a question to a category
 * @param {*} cat_Id the id of the category to which we are adding a question 
 * @returns here to break out of the function in case of unexpected behavior 
 */
function addQuestion(cat_Id) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category)
        return;
    const q_Id = uid();
    category.items.push({ id: q_Id, text: '', type: '', answer: [] });
    renderQuestions(cat_Id);
    markDirty()
}

/**
 *  Remove a question from the quiz
 * @param {*} cat_Id the id of the category to which we remove the question
 * @param {*} q_Id the id of the question which we are removing
 * @returns here to break out of the function in case of unexpected behavior 
 */
function removeQuestion(cat_Id, q_Id) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category)
        return;
    category.items = category.items.filter(q => q.id !== q_Id);
    if (active_question_Id === q_Id) {
        active_question_Id = null;
        closeAnswerPanel();
    }
    renderQuestions(cat_Id);
    markDirty()
}


/**
 * Change the inner text of a question 
 * @param {*} cat_Id cat_Id the id of the category to which we change the question
 * @param {*} q_Id the id of the question which we are changing
 * @param {*} new_Text what the question will now be
 * @returns here to break out of the function in case of unexpected behavior 
 */
function changeQuestionText(cat_Id, q_Id, new_Text) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category)
        return;
    const question = category.items.find(q => q.id === q_Id);
    if (question)
        question.text = new_Text;
    markDirty()
}

/**
 * Render a specific question
 * @param {*} cat_Id cat_Id the id of the category, of the question, that we are rendering
 * @returns here to break out of the function in case of unexpected behavior 
 */
function renderQuestions(cat_Id) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category)
        return;

    const container = document.getElementById('questions_list');
    if (!category.items.length) {
        container.innerHTML = `<p class="no_questions">No questions yet. Add one below.</p>`;
        return;
    }

    //add the question proper to the inner html, everything before is setting it up
    container.innerHTML = category.items.map((q, index) => `
            <div class="question_item${active_question_Id === q.id ? ' active' : ''}" data-id="${q.id}" onclick="openAnswerPanel('${cat_Id}', '${q.id}')">
            <span class="question_number">Q${index + 1}</span>
            <input
                class="question_input"
                value="${q.text}"
                placeholder="Type your question here"
                oninput="changeQuestionText('${cat_Id}', '${q.id}', this.value)"
                onclick="event.stopPropagation()"
            />
            <button class="remove_question" onclick="event.stopPropagation(); removeQuestion('${cat_Id}', '${q.id}')">✕</button>
        </div>
    `).join('');
}


/**
 * render a category, in the left side editor, the content itself will be rendered when the user click on it
 */
function renderCategory() {
    const container = document.getElementById('category');
    container.innerHTML = quiz.categories.map((category, index) => `
        <div class="category_item${active_category_Id === category.id ? ' active' : ''}" data-id="${category.id}" onclick="openEditor('${category.id}')">
            <span class="category_number">${index + 1}</span>
            <input
                class="category_name_input"
                value="${category.name}"
                oninput="changeCategoryName('${category.id}', this.value)"
                onclick="event.stopPropagation()"
                placeholder="category name"
            />
            <button class="remove_category" onclick="event.stopPropagation(); removeCategory('${category.id}')">✕</button>
        </div>
    `).join('');
}


/**
 * save the quiz, by sending the "quiz" dict to the backend, and saving that as a json object
 * @returns here to break out of the function in case of unexpected behavior(here no title)
 */
function saveQuiz() {
    if (!quiz.title) {
        alert("You have not chosen the name of your quiz. Please do so before saving it");
        return;
    }
    const jsonString = JSON.stringify(quiz, null, 2);

    fetch('/save_quiz', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: jsonString
    })
        .then(response => response.json())
        .then(data => {
            if (data.redirect) {
                window.location.href = data.redirect;
            }
        });
    markClean();
}


/**
 * Open the right side editor, allowing you to add answer, as well as type, to/of the quiz
 * @param {*} cat_Id the category to which the quiz belong
 * @param {*} q_Id the question to which the answer belong
 * @returns here to break out of the function in case of unexpected behavior 
 */
function openAnswerPanel(cat_Id, q_Id) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category)
        return;
    const question = category.items.find(q => q.id === q_Id);
    if (!question)
        return;

    active_question_Id = q_Id;

    document.querySelectorAll('.question_item').forEach(el => el.classList.remove('active'));
    const activeEl = document.querySelector(`.question_item[data-id="${q_Id}"]`);
    if (activeEl)
        activeEl.classList.add('active');

    document.getElementById('answer_panel').style.display = 'flex';
    renderAnswerPanel(cat_Id, q_Id);
}


/**
 * close the pannel, remove the highlight around the question
 */
function closeAnswerPanel() {
    document.getElementById('answer_panel').style.display = 'none';
    document.querySelectorAll('.question_item').forEach(el => el.classList.remove('active'));
    active_question_Id = null;
}


/**
 * Allow a user to change the type of a question
 * @param {*} cat_Id category of the question
 * @param {*} q_Id question to which we change the type of (right now you have two choice, we want to expand upon that) We may have a 3rd soon
 * @param {*} new_type the new type of the question
 * @returns here to break out of the function in case of unexpected behavior 
 */
function setQuestionType(cat_Id, q_Id, new_type) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category)
        return;
    const question = category.items.find(q => q.id === q_Id);
    if (!question)
        return;
    question.type = new_type;
    if (new_type === 'text')
        question.answer = [];
    if (new_type === 'mc' && !question.answer.length)
        question.answer = [{ id: uid(), text: '' }];
    if (new_type === 'sldr' && !question.answer.length)
        question.answer = [{ id: uid(), text: '' }];
    renderAnswerPanel(cat_Id, q_Id);
    markDirty()
}


/**
 * Add an answer to a question
 * @param {*} cat_Id category of the question
 * @param {*} q_Id question to which we add an answer
 * @returns here to break out of the function in case of unexpected behavior 
 */
function addAnswer_(cat_Id, q_Id) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category)
        return;
    const question = category.items.find(q => q.id === q_Id);
    if (!question)
        return;
    question.answer.push({ id: uid(), text: '' });
    renderAnswerPanel(cat_Id, q_Id);
    markDirty()
}


/**
 * Remove an answer to a question
 * @param {*} cat_Id category of the question
 * @param {*} q_Id question to which we remove an answer
 * @param {*} opt_Id the answer we remove
 * @returns here to break out of the function in case of unexpected behavior 
 */
function removeAnswer(cat_Id, q_Id, opt_Id) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category)
        return;
    const question = category.items.find(q => q.id === q_Id);
    if (!question)
        return;
    question.answer = question.answer.filter(o => o.id !== opt_Id);
    renderAnswerPanel(cat_Id, q_Id);
    markDirty()
}


/**
 * Changing text of an answer
 * @param {*} cat_Id category of the question
 * @param {*} q_Id question to which we change the answer
 * @param {*} opt_Id the answer we change
 * @param {*} new_text the new text of the answer
 * @returns here to break out of the function in case of unexpected behavior 
 */
function changeAnswerText(cat_Id, q_Id, opt_Id, new_text) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category)
        return;
    const question = category.items.find(q => q.id === q_Id);
    if (!question)
        return;
    const answer = question.answer.find(o => o.id === opt_Id);
    if (answer)
        answer.text = new_text;
    markDirty()
}


/**
 * Render the right side panel when you click on a question
 * @param {*} cat_Id category of the question
 * @param {*} q_Id the question to which we see the panel
 * @returns here to break out of the function in case of unexpected behavior 
 */
function renderAnswerPanel(cat_Id, q_Id) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category)
        return;
    const question = category.items.find(q => q.id === q_Id);
    if (!question)
        return;

    const is_text = question.type === 'text';
    const is_mc = question.type === 'mc';
    const is_sldr = question.type === 'sldr';

    // TODO maybe find a fix for this ? as it stand it wont stop until it cannot find ASCII character, however it mean at one point you stop having capital letter and just have char 
    const answers_html = is_mc || is_sldr ? `
        <div class="answers_list">
            ${question.answer.map((opt, i) => `
                <div class="answer_item">
                    <span class="answer_letter">${String.fromCharCode(65 + i)}</span>
                    <input
                        class="answer_input"
                        value="${opt.text}"
                        placeholder="answer ${String.fromCharCode(65 + i)}"
                        oninput="changeAnswerText('${cat_Id}', '${q_Id}', '${opt.id}', this.value)"
                    />
                    <span class="answer-leadsto-indicator"></span>
                    <button class="remove_answer" onclick="removeAnswer('${cat_Id}', '${q_Id}', '${opt.id}')">✕</button>
                </div>
            `).join('')}
        </div>
        <button class="add_answer_btn" onclick="addAnswer_('${cat_Id}', '${q_Id}')">Add answer</button>
    ` : `
        <div class="open_text_preview">
            <p>Respondents will type a free-form answer.</p>
            <div class="open_text_mock">Answer</div>
        </div>
    `;

    document.getElementById('answer_panel').innerHTML = `
        <div id="answer_panel_header">
            <span id="answer_panel_title">Answer setup</span>
            <button id="close_answer_panel" onclick="closeAnswerPanel()">✕</button>
        </div>
        <div id="answer_panel_body">
            <p class="panel_label">Question type</p>
            <div class="type_picker">
                <button class="type_btn${is_text ? ' selected' : ''}" onclick="setQuestionType('${cat_Id}', '${q_Id}', 'text')">Open text</button>
                <button class="type_btn${is_mc ? ' selected' : ''}" onclick="setQuestionType('${cat_Id}', '${q_Id}', 'mc')">Multiple choice</button>
                <button class="type_btn${is_sldr ? ' selected' : ''}" onclick="setQuestionType('${cat_Id}', '${q_Id}', 'sldr')">Slider</button>
            </div>
            <div id="answer_config">${answers_html}</div>
        </div>
    `;

    // if multiple choice, show the leadstos
    if (is_mc) {
        const allQuestions = quiz.categories.flatMap(cat => cat.items);
        question.answer.forEach((a, i) => {
            const indicators = document.querySelectorAll('#answer_panel .answer-leadsto-indicator');
            const target = allQuestions.find(q => q.id === a.leads_to);
            if (indicators[i]) indicators[i].textContent = target ? `⇒ ${target.text || '(unnamed)'}` : '';
        });
    }

}


/**
 * Broke off render into multiple functions in order to avoid cluttering, and for an easier experience reading the code
 */

function render() {
    if (quiz.title) {
        document.title = quiz.title;
    }
    getQuizInfo();
    renderCategory();
}


function openShare() {
    document.getElementById('share_overlay').style.display = 'flex';
    document.getElementById('share_message').style.display = 'none';
    loadAccessList();
}

function openBranching() {
    document.getElementById('branching_overlay').style.display = 'flex';

    const hasNodes = Object.keys(editor.export().drawflow.Home.data).length > 0;
    if (!hasNodes) {
        loadQuizIntoDrawflow();
    }
}

function closeBranching() {
    document.getElementById('branching_overlay').style.display = 'none';
}

function closeShare() {
    document.getElementById('share_overlay').style.display = 'none';
}

window.onclick = function (event) {
    var overlay_share = document.getElementById('share_overlay');
    var overlay_display = document.getElementById('branching')
    if (event.target == overlay_share) {
        overlay_share.style.display = 'none';
    }
    if (event.target == overlay_display) {
        overlay_display.stile.display = 'none';
    }
}
document.getElementById('delete_overlay').addEventListener('click', function (e) {
    if (e.target === this)
        closeDelete();
});
/**
 * Submit the share request
 * @returns here to break in case someone doesnt choose a username
 */
async function submitShare() {
    if (quiz.title && !window.location.href.includes("new_quiz")) {
        const username = document.getElementById('share_username').value.trim();
        const msg = document.getElementById('share_message');
        if (!username) {
            msg.innerHTML = "Please choose a username before submitting"
            return;
        }
        const response = await fetch("/quiz_share", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, quiz_id: quiz.id, role: document.getElementById('share_role')?.value || 'reader' })
        });

        const result = await response.json();
        msg.style.display = 'block';
        msg.style.color = result.error ? 'red' : 'green';
        if (result.error) {
            msg.innerHTML = result.error
        }
        else {
            msg.textContent = result.success;
        }

        if (!result.error) {
            document.getElementById('share_username').value = '';
            loadAccessList()
        }
    }
    else
        alert("Please choose a title and save your quiz before trying to share it")
}
/**
 * Load from the backend the exact user who have access to this quiz
 */
async function loadAccessList() {
    const list = document.getElementById('access_list');
    list.innerHTML = '<li class="access_list_loading">Loading…</li>';

    const response = await fetch(`/quiz_share?quiz_id=${quiz.id}`);
    const result = await response.json();

    if (!result.users || result.users.length === 0) {
        list.innerHTML = `<li class="access_list_empty">No one else has access yet.</li>`;
        return;
    }

    list.innerHTML = result.users.map(entry => {
        const isYou = entry.username === result.current_user;
        const youTag = isYou ? ' <em>(you)</em>' : '';


        const roleBadge = `<span class="access_tag role_badge--${entry.role}">${entry.role}</span>`;


        let rolePicker = '';
        if (result.can_share && entry.role !== 'creator' && !isYou) {
            const opts = ['reader', 'editor', 'admin']
                .filter(r => {
                    // admin actors cannot assign admin
                    if (_role === 'admin' && r === 'admin') return false;
                    return true;
                })
                .map(r => `<option value="${r}"${r === entry.role ? ' selected' : ''}>${r}</option>`)
                .join('');
            rolePicker = `
                <select class="role_select_inline"
                        onchange="changeUserRole('${entry.username}', this.value, this)">
                    ${opts}
                </select>`;
        }

        // Revoke button
        const revokeBtn = entry.can_revoke
            ? `<button class="revoke_btn" onclick="revokeAccess('${entry.username}')">Remove</button>`
            : '';

        return `<li class="access_list_item">
            <span>${entry.username}${youTag}</span>
            ${roleBadge}
            ${rolePicker}
            ${revokeBtn}
        </li>`;
    }).join('');
}
async function revokeAccess(username) {
    const msg = document.getElementById('share_message');
    const response = await fetch('/quiz_revoke', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, quiz_id: quiz.id })
    });
    const result = await response.json();
    msg.style.display = 'block';
    msg.style.color = result.error ? 'red' : 'green';
    msg.innerHTML = result.error || result.success;
    if (!result.error)
        loadAccessList();
}

async function changeUserRole(username, newRole, selectEl) {
    const msg = document.getElementById('share_message');
    const response = await fetch('/quiz_update_role', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, quiz_id: quiz.id, role: newRole })
    });
    const result = await response.json();
    msg.style.display = 'block';
    msg.style.color = result.error ? 'red' : 'green';
    msg.innerHTML = result.error || result.success;
    if (result.error && selectEl)
        loadAccessList(); // revert picker on error
}
/**
 * Allow for a preview of the quiz. I did this instead of the simple url_for, as it allowed for easier verification that the quiz had been saved at least once.
 */
function previewQuiz() {
    if (quiz.title && !window.location.href.includes("new_quiz"))
        window.location.href = `/quiz_preview/${quiz.id}`;
    else
        alert("Please choose a title and save your quiz before trying to preview it")
}

function openDelete() {
    document.getElementById('delete_overlay').style.display = 'flex';
}

function closeDelete() {
    document.getElementById('delete_overlay').style.display = 'none';
}

async function deleteQuiz() {
    if (!quiz.title && window.location.href.includes("new_quiz")) {
        alert("Your quiz has not even been saved once, and as such does not need to be deleted, you can just refresh the page.")
        closeDelete()
        return
    }
    const response = await fetch('/quiz_delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quiz_id: quiz.id })
    });
    const result = await response.json()
    if (!result.error) {
        window.location.href = result.redirect;

    }
    else {
        alert(result.error)
    }
}
// having render here ensure that everything is shown properly, as it will render everything once when the page is loaded for the first time
render();










// Branching section:
var id = document.getElementById("drawflow");
const editor = new Drawflow(id);
editor.reroute = true;
editor.start();
editor.editor_mode = 'edit';

const questionTemplate = `
    <div class="question-node">
      <input class="question-title drawflow-input" type="text" placeholder="Question text" />
      <div class="answers">
        <div class="answer" data-output="output_1">
          <input type="text" class="drawflow-input" placeholder="Option 1" />
          <button class="remove-answer" onclick="removeNodeAnswer(this)">-</button>
        </div>
        <div class="answer" data-output="output_2">
          <input type="text" class="drawflow-input" placeholder="Option 2" />
          <button class="remove-answer" onclick="removeNodeAnswer(this)">-</button>
        </div>
      </div>
      <button class="add-answer" onclick="addNodeAnswer(this)">+</button>
    </div>
`;

const endTemplate = `
    <div class="end-node">
      <input class="end-title drawflow-input" type="text" placeholder="Result" />
    </div>
`;

function getQuizQuestion(nodeId) {
    const node = editor.getNodeFromId(nodeId);
    const allQuestions = quiz.categories.flatMap(cat => cat.items);
    return allQuestions.find(q => q.id === node.data.question_id) || null;
}

function addNodeAnswer(btn) {
    const answers = btn.previousElementSibling;
    const nodeEl = btn.closest('.drawflow-node');
    const nodeId = nodeEl.id.replace('node-', '');
    const node = editor.getNodeFromId(nodeId);

    const outputKeys = Object.keys(node.outputs);
    const maxNum = outputKeys.reduce((max, key) => {
        const num = parseInt(key.replace('output_', ''));
        return num > max ? num : max;
    }, 0);
    const outputKey = `output_${maxNum + 1}`;
    editor.addNodeOutput(nodeId);

    const question = getQuizQuestion(nodeId);
    if (question) {
        question.answer.push({ id: uid(), text: '', leads_to: null });
    }

    const div = document.createElement('div');
    div.classList.add('answer');
    div.dataset.output = outputKey;
    div.innerHTML = `
        <input type="text" class="drawflow-input" placeholder="Option ${maxNum + 1}" oninput="updateAnswerText(this)"/>
        <button class="remove-answer" onclick="removeNodeAnswer(this)">-</button>`;
    answers.appendChild(div);

    renumberAnswers(nodeEl);
}

function removeNodeAnswer(btn) {
    const answer = btn.parentElement;
    const nodeEl = btn.closest('.drawflow-node');
    const nodeId = nodeEl.id.replace('node-', '');
    const answers = answer.parentElement;

    if (answers.children.length <= 1) return;

    const outputKey = answer.dataset.output;
    const node = editor.getNodeFromId(nodeId);

    const connections = [...(node.outputs[outputKey]?.connections || [])];
    connections.forEach(conn => {
        editor.removeSingleConnection(nodeId, conn.node, outputKey, conn.output);
    });

    const outputEl = document.querySelector(`#node-${nodeId} .outputs .${outputKey}`);
    if (outputEl) outputEl.remove();
    delete node.outputs[outputKey];

    const answerIndex = parseInt(outputKey.replace('output_', '')) - 1;
    const question = getQuizQuestion(nodeId);
    if (question) {
        question.answer.splice(answerIndex, 1);
    }

    answer.remove();
    renumberAnswers(nodeEl);
}

document.querySelectorAll('.node-type').forEach(el => {
    el.addEventListener('dragstart', e => {
        e.dataTransfer.setData('node-type', e.target.dataset.node);
    });
});

document.getElementById('drawflow').addEventListener('dragover', e => e.preventDefault());

document.getElementById('drawflow').addEventListener('drop', e => {
    e.preventDefault();
    const type = e.dataTransfer.getData('node-type');
    if (!type) return;

    const precanvas = editor.precanvas;
    const zoom = editor.zoom;

    let pos_x = e.clientX * (precanvas.clientWidth / (precanvas.clientWidth * zoom))
        - (precanvas.getBoundingClientRect().x * (precanvas.clientWidth / (precanvas.clientWidth * zoom)));

    let pos_y = e.clientY * (precanvas.clientHeight / (precanvas.clientHeight * zoom))
        - (precanvas.getBoundingClientRect().y * (precanvas.clientHeight / (precanvas.clientHeight * zoom)));

    if (type == 'question') {
        editor.addNode('question', 1, 2, pos_x, pos_y, 'question', {}, questionTemplate);
    } else if (type == 'end') {
        editor.addNode('end', 1, 0, pos_x, pos_y, 'end', {}, endTemplate);
    }
});

editor.on('connectionCreated', function (info) {
    const node = editor.getNodeFromId(info.output_id);
    const connections = node.outputs[info.output_class].connections;

    if (connections.length > 1) {
        const old = connections[0];
        editor.removeSingleConnection(info.output_id, old.node, info.output_class, old.output);
    }

    document.getElementById('node-' + info.input_id).getElementsByClassName(info.input_class)[0].classList.add('inputConnected');

    const answerIndex = parseInt(info.output_class.replace('output_', '')) - 1;
    const targetNode = editor.getNodeFromId(info.input_id);
    const question = getQuizQuestion(info.output_id);
    if (question?.answer[answerIndex]) {
        question.answer[answerIndex].leads_to = targetNode.data.question_id || null;
    }

    const allQuestions = quiz.categories.flatMap(cat => cat.items);
    const target = allQuestions.find(q => q.id === targetNode.data.question_id);
    const indicators = document.querySelectorAll('#answer_panel .answer-leadsto-indicator');
    if (indicators[answerIndex])
        indicators[answerIndex].textContent = target ? `⇒ ${target.text || '(unnamed)'}` : '';
});

editor.on("connectionRemoved", function (info) {
    const node = editor.getNodeFromId(info.input_id);
    const connections = node.inputs[info.input_class].connections;

    if (connections.length === 0) {
        document.getElementById('node-' + info.input_id).getElementsByClassName(info.input_class)[0].classList.remove('inputConnected');
    }

    const answerIndex = parseInt(info.output_class.replace('output_', '')) - 1;
    const question = getQuizQuestion(info.output_id);
    if (question?.answer[answerIndex]) {
        question.answer[answerIndex].leads_to = null;
    }

    const indicators = document.querySelectorAll('#answer_panel .answer-leadsto-indicator');
    if (indicators[answerIndex])
        indicators[answerIndex].textContent = "";
});

function renumberAnswers(nodeEl) {
    const answers = nodeEl.querySelectorAll('.answer input');
    answers.forEach((input, i) => {
        input.placeholder = `Option ${i + 1}`;
    });
}

function loadQuizIntoDrawflow() {
    editor.clearModuleSelected();

    const allQuestions = quiz.categories.flatMap(cat => cat.items);
    const nodeIds = [];

    allQuestions.forEach((q, i) => {
        const x = i * 350 + 50;
        // TODO: position nodes in a tree structure! when its linear it makes everything hard to visually parse.
        // not sure how to tackle that tbh... programmatically decide y value based on number of leadsto somehow maybe?
        const y = 200;

        const answers_html = q.answer.map((a, j) => `
    <div class="answer" data-output="output_${j + 1}">
        <input type="text" class="drawflow-input" placeholder="Option ${j + 1}" value="${a.text || ''}" oninput="updateAnswerText(this)"/>
        <button class="remove-answer" onclick="removeNodeAnswer(this)">-</button>
    </div>
`).join('');

        const template = `
    <div class="question-node">
        <input class="question-title drawflow-input" type="text" placeholder="Question text" value="${q.text || ''}" oninput="updateQuestionText(this)"/>
        <div class="answers">${answers_html}</div>
        <button class="add-answer" onclick="addNodeAnswer(this)">+</button>
    </div>
`;

        const numOutputs = q.answer.length;
        const nodeId = editor.addNode(
            'question', 1, numOutputs,
            x, y,
            'question', { question_id: q.id }, template
        );

        nodeIds.push(nodeId);
    });

    setTimeout(() => {
        const questionToNode = {};
        nodeIds.forEach((nodeId, i) => {
            const node = editor.getNodeFromId(nodeId);
            questionToNode[node.data.question_id] = nodeId;
        });

        allQuestions.forEach((q, i) => {
            const sourceNodeId = questionToNode[q.id];
            q.answer.forEach((a, j) => {
                const outputKey = `output_${j + 1}`;
                if (a.leads_to && questionToNode[a.leads_to]) {
                    editor.addConnection(sourceNodeId, questionToNode[a.leads_to], outputKey, 'input_1');
                } else if (!a.leads_to && nodeIds[i + 1]) {
                    editor.addConnection(sourceNodeId, nodeIds[i + 1], outputKey, 'input_1');
                }
            });
        });
    }, 100);
}

editor.on('nodeCreated', function (nodeId) {
    const node = editor.getNodeFromId(nodeId);
    if (node.name !== 'question') return;
    if (node.data.question_id) return;

    const q_id = uid();
    const newQuestion = {
        id: q_id, text: '', type: 'mc',
        answer: [
            { id: uid(), text: '', leads_to: null },
            { id: uid(), text: '', leads_to: null }
        ]
    };

    editor.drawflow.drawflow.Home.data[nodeId].data.question_id = q_id;
    quiz.categories[0].items.push(newQuestion);

    const answers_html = newQuestion.answer.map((a, j) => `
        <div class="answer" data-output="output_${j + 1}">
            <input type="text" class="drawflow-input" placeholder="Option ${j + 1}" value="" oninput="updateAnswerText(this)"/>
            <button class="remove-answer" onclick="removeNodeAnswer(this)">-</button>
        </div>
    `).join('');

    const nodeEl = document.querySelector(`#node-${nodeId} .drawflow_content_node`);
    nodeEl.innerHTML = `
        <div class="question-node">
            <input class="question-title drawflow-input" type="text" placeholder="Question text" oninput="updateQuestionText(this)"/>
            <div class="answers">${answers_html}</div>
            <button class="add-answer" onclick="addNodeAnswer(this)">+</button>
        </div>
    `;
});

function updateQuestionText(input) {
    const nodeEl = input.closest('.drawflow-node');
    const nodeId = nodeEl.id.replace('node-', '');
    const question = getQuizQuestion(nodeId);
    if (question) question.text = input.value;
}

function updateAnswerText(input) {
    const nodeEl = input.closest('.drawflow-node');
    const nodeId = nodeEl.id.replace('node-', '');
    const question = getQuizQuestion(nodeId);
    if (!question) return;

    const answerEl = input.closest('.answer');
    const outputKey = answerEl.dataset.output;
    const answerIndex = parseInt(outputKey.replace('output_', '')) - 1;
    if (question.answer[answerIndex]) question.answer[answerIndex].text = input.value;
}



window.addEventListener('beforeunload', (event) => {
    if (isDirty) {
        event.preventDefault();
        event.returnValue = '';
    }
});