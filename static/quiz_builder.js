// class variable, alongside quiz (a dictionary), which is defined in quiz_builder.html
let active_category_Id = null;
let active_question_Id = null;


/**
 * helper function, create a random string to id the div
 */
function uid() {
    return Math.random().toString(36).slice(2, 9);
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
 * @param {*} q_Id question to which we change the type of (right now you have two choice, we want to expand upon that)
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
    renderAnswerPanel(cat_Id, q_Id);
}


/**
 * Add an answer to a question
 * @param {*} cat_Id category of the question
 * @param {*} q_Id question to which we add an answer
 * @returns here to break out of the function in case of unexpected behavior 
 */
function addAnswer(cat_Id, q_Id) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category)
        return;
    const question = category.items.find(q => q.id === q_Id);
    if (!question)
        return;
    question.answer.push({ id: uid(), text: '' });
    renderAnswerPanel(cat_Id, q_Id);
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

    // TODO maybe find a fix for this ? as it stand it wont stop until it cannot find ASCII character, however it mean at one point you stop having capital letter and just have char 
    const answers_html = is_mc ? `
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
                    <button class="remove_answer" onclick="removeAnswer('${cat_Id}', '${q_Id}', '${opt.id}')">✕</button>
                </div>
            `).join('')}
        </div>
        <button class="add_answer_btn" onclick="addAnswer('${cat_Id}', '${q_Id}')">Add answer</button>
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
            </div>
            <div id="answer_config">${answers_html}</div>
        </div>
    `;
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

//from here
function openShare() {
    document.getElementById('share_overlay').style.display = 'flex';
    document.getElementById('share_message').style.display = 'none';
    loadAccessList();
}

function closeShare() {
    document.getElementById('share_overlay').style.display = 'none';
}

window.onclick = function (event) {
    var overlay = document.getElementById('share_overlay');
    if (event.target == overlay) {
        overlay.style.display = 'none';
    }
}

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
            body: JSON.stringify({ username: username, quiz_id: quiz.id })
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

    const response = await fetch(`/quiz_share?quiz_id=${quiz.id}`);
    const result = await response.json();
    const isCreator = result.current_user === result.creator;

    if (!result.users || result.users.length === 0) {
        list.innerHTML = `<li class="access_list_empty">No one else has access yet.</li>`;
    } else {
        list.innerHTML = result.users.map(u => {
            const isYou = u === result.current_user;
            const isOwner = u === result.creator;
            const tag = isOwner ? ' (creator)' : '';
            const youTag = isYou ? ' (you)' : '';
            const revokeBtn = isCreator && !isOwner
                ? `<button class="revoke_btn" onclick="revokeAccess('${u}')">Remove</button>`
                : '';
            return `<li class="access_list_item">${u}${tag}${youTag}${revokeBtn}</li>`;
        }).join('');
    }
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
// to here 
// are function related to the share overlay button 

/**
 * Allow for a preview of the quiz. I did this instead of the simple url_for, as it allowed for easier verification that the quiz had been saved at least once.
 */
function previewQuiz() {
    if (quiz.title && !window.location.href.includes("new_quiz"))
        window.location.href = `/quiz_preview/${quiz.id}`;
    else
        alert("Please choose a title and save your quiz before trying to preview it")
}

// having render here ensure that everything is shown properly, as it will render everything once when the page is loaded for the first time
render();