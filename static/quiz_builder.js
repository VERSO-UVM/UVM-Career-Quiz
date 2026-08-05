// class variable, alongside quiz (a dictionary), which is defined in quiz_builder.html
let active_category_Id = null;
let active_question_Id = null;

//this variable should be marked true any single time a change happen to the quiz.
var isDirty = false;

// role of the user, it's fetched from app.py 
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
 * Not a function per se, allow for sorting the different category thanks to the sortableJS library. 
 */
new Sortable(document.getElementById('category'), {
    animation: 150,
    handle: '.category_item',
    onEnd: function (evt) {
        const [moved] = quiz.categories.splice(evt.oldIndex, 1);
        quiz.categories.splice(evt.newIndex, 0, moved);
        markDirty();
    }
});

/**
 * Used in conjunction with a button in the html, create a category upon which you can add question. The category is added to the quiz dict
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

// variable used with the sortableJS library
let questionSortable = null;

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
        if (questionSortable) {
            questionSortable.destroy();
            questionSortable = null;
        }
        return;
    }


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

    if (questionSortable) {
        questionSortable.destroy();
    }
    questionSortable = new Sortable(container, {
        animation: 150,
        handle: '.question_number',
        onEnd: function (evt) {
            if (evt.oldIndex === evt.newIndex) return;
            const [moved] = category.items.splice(evt.oldIndex, 1);
            category.items.splice(evt.newIndex, 0, moved);
            renderQuestions(cat_Id);
            markDirty();
        }
    });
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

    applySequentialLeadsTo();

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
            if (data.error) {
                alert(data.error);
            } else {
                quiz.id = data.id;
                quiz.last_modified = data.last_modified;
                markClean();
                if (window.location.href.includes("new_quiz")) {
                    window.location.href = `/quiz_builder/${data.id}`;
                }
            }
        });
}

// generates leadsto value based on sequential order if it has none yet.
function applySequentialLeadsTo() {
    const allQuestions = quiz.categories.flatMap(cat => cat.items);

    allQuestions.forEach((question, index) => {
        if (question.type === 'result') return
        const nextQuestion = allQuestions[index + 1];

        if (!question.answer) return;

        question.answer.forEach(answer => {
            // recompute every time unless the user manually wired this one in the branching editor
            if (answer.auto_leads_to !== false) {
                answer.leads_to = nextQuestion ? nextQuestion.id : null;
                answer.auto_leads_to = true;
            }
        });
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

    handleQuestionTypeChange(new_type, cat_Id, q_Id, question);

    question.type = new_type;
    if (new_type === 'text' && !question.answer.length)
        question.answer = [{ id: uid(), text: '', leads_to: null }];
    if (new_type === 'mc' && !question.answer.length)
        question.answer = [{ id: uid(), text: '' }];
    if (new_type === 'sldr' && !question.answer.length)
        question.answer = [{ id: uid(), text: '' }];
    if (new_type === 'result' && !question.answer.length)
        question.answer = [{ id: uid(), text: '', leads_to: null }];
    if (new_type === 'drag' && !question.answer.length)
        question.answer = [{ id: uid(), text: '' }]; // <-- ADD is JSON text for answer format here
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
 * renders the drag drop question editor/maker
 * If the user is trying to edit an existing question then it will render the already existing 
 * @returns error if the panel doesn't exist
 */
function dragDropDesignPanel(){
    // Grab the modal element from quiz_builder.html
    const modal = document.getElementById('dragDropModal');
    if (!modal) {
        console.error("Error: #dragDropModal not found in the HTML DOM.");
        return;
    }

    // if there was already existing drags and drops in the panel render those onto the screen this is kind of bloated and will be cleaned up later but it all works
    for (const matchingCategory of quiz.categories) {
        if (matchingCategory.id === active_category_Id) {
            for (const matchingQuestion of matchingCategory.items) {
                if (matchingQuestion.id === active_question_Id) {
    
                    const dragsObj = matchingQuestion.answer.find(a => a.drags);
                    const dropsObj = matchingQuestion.answer.find(a => a.drops);
    
                    // Populate existing Drag Boxes
                    if (dragsObj?.drags) {
                        for (const drag of dragsObj.drags) {
                            addDraggableBox(drag);
                        }
                    }
    
                    // Populate existing Drop Boxes
                    if (dropsObj?.drops) {
                        for (const drop of dropsObj.drops) {
                            addDropBox(drop);
                        }
                    }
    
                }
            }
        }
    }
    // Reveal the modal overlay
    modal.style.display = 'flex';
}

/**
 * Adds draggable box to the editing screen to enter text into
 * @param {*} drag JSON element that contains an existing drag boxes text and id so the user can edit/view the contents
 * @returns error if no window is found
 */
function addDraggableBox(drag = null) {
    const dragBoxWindow = document.querySelector('.Drag-Box-Window');
    if (!dragBoxWindow) {
        console.error("Could not find .Drag-Box-Window on the page!");
        return;
    }

    const newDragBox = document.createElement('div');

    // Use the saved ID if editing, or generate a new random ID
    newDragBox.id = drag?.id || uid(); 
    newDragBox.classList.add('created-drop-item');

    // Determine default text or existing saved text
    const initialText = drag?.text || '';
    const defaultPlaceholder = 'Enter draggable answer here';

    // Build HTML with dynamic value setting and delete button
    newDragBox.innerHTML = `
        <span class="drop-label">Drag Box:</span>
        <input type="text" 
               class="drop-item-input" 
               value="${initialText}" 
               placeholder="${initialText ? '' : defaultPlaceholder}" 
               onfocus="this.placeholder = ''" 
               onblur="this.placeholder = this.value ? '' : '${defaultPlaceholder}'">
        <button type="button" class="remove-item-btn" onclick="this.parentElement.remove()">×</button>
    `;

    dragBoxWindow.appendChild(newDragBox);
}

/**
 * Adds drop box to the editing screen to enter text into
 * @param {*} drop JSON element that contains an existing drop boxes text and id so the user can edit/view the contents
 * @returns error if no window is found
 */
function addDropBox(drop = null) {
    const dropBoxWindow = document.querySelector('.Drop-Box-Window');
    if (!dropBoxWindow) {
        console.error("Could not find .Drop-Box-Window on the page!");
        return;
    }

    const newDropBox = document.createElement('div');

    // Use the saved ID if editing, or generate a new random ID
    newDropBox.id = drop?.id || uid(); 
    newDropBox.classList.add('created-drop-item');

    // Determine default text or existing saved text
    const initialText = drop?.text || '';
    const defaultPlaceholder = 'Enter drop box text here';

    // Build HTML with value setting and delete button
    newDropBox.innerHTML = `
        <span class="drop-label">Drop Box:</span>
        <input type="text" 
               class="drop-item-input" 
               value="${initialText}" 
               placeholder="${initialText ? '' : defaultPlaceholder}" 
               onfocus="this.placeholder = ''" 
               onblur="this.placeholder = this.value ? '' : '${defaultPlaceholder}'">
        <button type="button" class="remove-item-btn" onclick="this.parentElement.remove()">×</button>
    `;

    dropBoxWindow.appendChild(newDropBox);
}
/**
 * Gets users answers from the quiz question page
 * @param {*} windowName div that holds the text and id's of the drag and drop elements
 * @returns AnswerList formatted JSON elements that that used to store the users answers in the database
 */
function getBoxTextAndId(windowName){
    // Safety check to make sure a valid HTML element was passed in
    if (!windowName) return [];
    let AnswerList;

    const allDragBoxes = windowName.querySelectorAll('.created-drop-item');

    if (windowName.id === 'drop-box-window') {
        AnswerList = {drops: []}
        
    } else if (windowName.id === 'drag-box-window') {
        AnswerList = {drags: []}
    }
    
    for (const box of allDragBoxes) {
        const input = box.querySelector('.drop-item-input');
        if (input) {
            
            if (windowName.id === 'drop-box-window') {
                AnswerList.drops.push({
                    id: box.id,
                    text: input.value
                });
            } else if (windowName.id === 'drag-box-window') {
                AnswerList.drags.push({
                    id: box.id,
                    text: input.value
                });
            }
        }
    }
    return AnswerList; 
}

/**
 * Saves it to the JSON file in the proper format
 */
function saveDragDropQuestion(){
    // Find both windows on the page
    const dragBoxWindow = document.getElementById('drag-box-window');
    const dropBoxWindow = document.getElementById('drop-box-window');

    // Safety check to make sure the windows actually exist before reading them
    if (!dragBoxWindow || !dropBoxWindow) {
        console.error("Could not find the drag or drop windows on the page!");
        return;
    }

    let DROP_BoxTextAndIds = getBoxTextAndId(dropBoxWindow);
    let DRAG_BoxTextAndIds = getBoxTextAndId(dragBoxWindow);

    console.log("QuestionId: " + active_question_Id);
    console.log("CategoryId: " + active_category_Id);
    
    // Overwrite old answer
    for (const matchingCategory of quiz.categories){
        if(matchingCategory.id === active_category_Id){
            for(const matchingQuestion of matchingCategory.items){
                if(matchingQuestion.id === active_question_Id){
                    removeAnswer(active_category_Id, active_question_Id, matchingQuestion.answer.id);
                }
            }
        }
    }

    // Save new JSON answers
    for (const matchingCategory of quiz.categories){
        if(matchingCategory.id === active_category_Id){
            for(const matchingQuestion of matchingCategory.items){
                if(matchingQuestion.id === active_question_Id){
                    matchingQuestion.answer.push(DRAG_BoxTextAndIds);  
                    matchingQuestion.answer.push(DROP_BoxTextAndIds);
                }
            }
        }
    }
    closeModal();
}

/**
 * Hides the drag drop modal overlay and resets its inputs
 */
function closeModal() {
    const modal = document.getElementById('dragDropModal');
    modal.style.display = 'none';
}

/**
 * If the admin wants to change a 'darg' question to any other question type 
 * this function deletes the JSON elements for the drags and drops
 * 
 * @param {*} categoryId Current category id of the question
 * @param {*} questionId Current question id 
 * @returns error if the question id isn't found
 */
function removeDragAndDropData(categoryId, questionId) {
    // Find the target category
    const category = quiz.categories.find(cat => cat.id === categoryId);
    if (!category) {
        console.error(`Category with ID ${categoryId} not found.`);
        return;
    }

    // Find the target question within that category
    const question = category.items.find(q => q.id === questionId);
    if (!question || !Array.isArray(question.answer)) {
        console.error(`Question with ID ${questionId} not found or missing answer array.`);
        return;
    }

    // Filter out objects containing 'drags' or 'drops' properties
    question.answer = question.answer.filter(item => !item.drags && !item.drops);
}

/**
 * This function checks for if the new question type is not 'drag' and will call the removeDragAndDropData function
 * to make sure that if the question was previously 'drag' that it reformats correctly in the JSON
 * 
 * Currently this is only for 'drag' questions but when new question types are added more remove functions can be put here
 * 
 * @param {*} newType The new question type that the question is set to
 * @param {*} cat_Id Current category id of the question
 * @param {*} q_id Current question id
 * * @param {*} question Current question object
 */
function handleQuestionTypeChange(newType, cat_Id, q_id, question) {
    // Check if user is changing away from drag & drop
    if (newType !== 'drag') {
        // Remove drags and drops from the JSON structure
        removeDragAndDropData(cat_Id, q_id);
        console.log(`Drag & drop data cleared.`);
        
    } else if (newType === 'drag'){
        for(const ans of question.answer){
            removeAnswer(cat_Id, q_id, ans.id);
        }
    }
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
    const is_result = question.type === 'result'
    const is_drag = question.type === 'drag'

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
    `: is_result ? `
       <div class="open_text_preview">
        <textarea class="result_body" placeholder="Body text (optional)" oninput="changeResultBody('${cat_Id}', '${q_Id}', this.value)">${question.result_body || ''}</textarea>
        <label class="email_append_label">
            <input type="checkbox" class="email_append_checkbox" ${question['email-append'] ? 'checked' : ''} onchange="toggleEmailAppend('${cat_Id}', '${q_Id}', this.checked)" />
            Append to email?
        </label>
        ${question['email-append'] ? `
        <textarea class="email_append_text" placeholder="Text to append to email (optional)" oninput="changeEmailAppendText('${cat_Id}', '${q_Id}', this.value)">${question['email-append-text'] || ''}</textarea>
        ` : ''}
    </div>
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
                <button class="type_btn${is_text ? ' selected' : ''}" onclick="setQuestionType('${cat_Id}', '${q_Id}', 'text')">Free Response</button>
                <button class="type_btn${is_mc ? ' selected' : ''}" onclick="setQuestionType('${cat_Id}', '${q_Id}', 'mc')">Multiple choice</button>
                <button class="type_btn${is_sldr ? ' selected' : ''}" onclick="setQuestionType('${cat_Id}', '${q_Id}', 'sldr')">Slider</button>
                <button class="type_btn${is_result ? ' selected' : ''}" onclick="setQuestionType('${cat_Id}', '${q_Id}', 'result')">No Response</button>

                <button class="type_btn${is_drag ? ' selected' : ''}" onclick="setQuestionType('${cat_Id}', '${q_Id}', 'drag'); dragDropDesignPanel()">Drag & Drop</button>
  
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
            if (indicators[i]) indicators[i].textContent = target ? `⇒ ${target.text || '(unnamed)'} ` : '';
        });
    }

}


/**
 * change a result
 * @param {*} cat_Id the category that the question belong too
 * @param {*} q_Id the question that we are changing 
 * @param {*} new_text the new text of the result
 * @returns espace the function in case of unexpected behavior
 */
function changeResultBody(cat_Id, q_Id, new_text) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category) return;
    const question = category.items.find(q => q.id === q_Id);
    if (!question) return;
    question.result_body = new_text;
    markDirty();
}

function toggleEmailAppend(cat_Id, q_Id, checked) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category) return;
    const question = category.items.find(q => q.id === q_Id);
    if (!question) return;
    question['email-append'] = checked;
    markDirty();
    renderAnswerPanel(cat_Id, q_Id); // re-render so the textarea appears/disappears
}

function changeEmailAppendText(cat_Id, q_Id, new_text) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category) return;
    const question = category.items.find(q => q.id === q_Id);
    if (!question) return;
    question['email-append-text'] = new_text;
    markDirty();
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

/**
 * Allow for a preview of the quiz. It need to be saved at least once.
 */
function previewQuiz() {
    if (quiz.title && !window.location.href.includes("new_quiz"))
        window.location.href = `/quiz_preview/${quiz.id}`;
    else
        alert("Please choose a title and save your quiz before trying to preview it")
}

//EVERYTHING FROM THIS COMMENT TO THE NEXT SUCH COMMENT IS RELATED TO OPENING AND CLOSING OF THE BRANCHING OVERLAY

/**
 * Function much the same as the share overlay (if a bit more complicated), open the branching overlay 
 */
function openBranching() {
    document.getElementById('branching_overlay').style.display = 'flex';
    // snapshot quiz state before any drawflow edits
    drawflowSnapshot = JSON.parse(JSON.stringify(quiz));

    deletedQuestionIds.clear();
    Object.keys(nodeQuestionMap).forEach(i => delete nodeQuestionMap[i]);

    const hasNodes = Object.keys(editor.export().drawflow.Home.data).length > 0;
    if (!hasNodes) {
        loadQuizIntoDrawflow();
    }
}

/**
 * close the branching overlay, by flipping the css around, and closing the drawflow.
 * @returns espace in case of unwanted behavior
 */
function closeBranching() {
    if (drawflowSnapshot && drawflowDirty) {
        if (!confirm('Are you sure you want to close? Unsaved changes will be lost.'))
            return;
        quiz.categories = drawflowSnapshot.categories;
        deletedQuestionIds.clear();
        Object.keys(nodeQuestionMap).forEach(i => delete nodeQuestionMap[i]);
    }
    drawflowSnapshot = null;
    drawflowDirty = false;
    document.getElementById('branching_overlay').style.display = 'none';
}


//EVERYTHING INVOLVING IN THE SHARE OVERLAY IS FROM HERE TO THE NEXT COMMENT SUCH AS THIS ONE

/**
 * Open the share overlay, useless by itself, it work by modifing the coresponding css. 
 */
function openShare() {
    document.getElementById('share_overlay').style.display = 'flex';
    document.getElementById('share_message').style.display = 'none';
    loadAccessList();
}


/**
 * Close the share overlay by flipping css value around
 */
function closeShare() {
    document.getElementById('share_overlay').style.display = 'none';
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
 * Load from the backend the exact users who have access to this quiz
 */
async function loadAccessList() {
    const list = document.getElementById('access_list');
    list.innerHTML = '<li class="access_list_loading">Loading...</li>';

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
                    if (_role === 'admin' && r === 'admin') return false;
                    return true;
                })
                .map(r => `<option value = "${r}"${r === entry.role ? ' selected' : ''}> ${r}</option> `)
                .join('');
            rolePicker = `
        <select class="role_select_inline"
    onchange = "changeUserRole('${entry.username}', this.value)">
        ${opts}
                </select> `;
        }


        const revokeBtn = entry.can_revoke
            ? `<button class="revoke_btn" onclick = "revokeAccess('${entry.username}')"> Remove</button > `
            : '';

        return `<li class="access_list_item">
        <span>${entry.username}${youTag}</span>
            ${roleBadge}
            ${rolePicker}
            ${revokeBtn}
        </li> `;
    }).join('');
}

/**
 * If the user revoking acess has the sufficient level of authorization, revoke the acess of the other user
 * @param {*} username the username of the user who will not be allowed access anymore 
 */
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

/**
 * Change the role of a user (provided the present user has the corect permission)
 * @param {*} username the username who's role will be changed 
 * @param {*} newRole the new role of the user
 */
async function changeUserRole(username, newRole) {
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
    if (result.error)
        loadAccessList();
}


// EVERYTHING INVOLVED IN THE ASSIGN OVERLAY IS FROM HERE TO THE NEXT COMMENT SUCH AS THIS ONE

/**
 * Open the assign overlay
 */
function openAssign() {
    document.getElementById('assign_overlay').style.display = 'flex';
    document.getElementById('assign_message').style.display = 'none';
}

/**
 * Closet the assign overlay
 */
function closeAssign() {
    document.getElementById('assign_overlay').style.display = 'none';
}


/**
 * Submit an assignment. This function will assign a quiz to a user/group of user.
 * @returns escape in case of unwanted behavior
 */
async function submitAssign() {
    if (quiz.title && !window.location.href.includes("new_quiz")) {
        const username = document.getElementById('assign_username').value.trim();
        const msg = document.getElementById('assign_message');
        if (!username) {
            msg.style.display = 'block';
            msg.style.color = 'red';
            msg.innerHTML = 'Please enter a username before submitting';
            return;
        }

        const response = await fetch('/assign_quiz', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: username, quiz_id: quiz.id })
        });
        const result = await response.json();
        msg.style.display = 'block';
        msg.style.color = result.error ? 'red' : 'green';
        msg.innerHTML = result.error || result.success;
        if (!result.error) {
            document.getElementById('assign_username').value = '';
        }
    }
    else
        alert("Please choose a title and save your quiz before trying to assign it")
}


// EVERYTHING INVOLVED IN THE DELETE OVERLAY IS FROM HERE TO THE WINDOW.ONCLICK FUNCTION

/**
 * Open the delete overlay
 */
function openDelete() {
    document.getElementById('delete_overlay').style.display = 'flex';
}

/**
 * Close the delete overlay
 */
function closeDelete() {
    document.getElementById('delete_overlay').style.display = 'none';
}

/**
 * Delete a quiz. Should be checked again in app.py.
 * @returns in case of unwanted behavior
 */
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

/**
 * this is here for the overlays (Add to this function for each overlay created), it will allow for closure of the overlay if the user click outside of it.
 * TODO if you create an overlay and it's associated close function, use them acordingly here.
 * @param {*} event 
 */
window.onclick = function (event) {
    var overlay_share = document.getElementById('share_overlay');
    var overlay_display = document.getElementById('branching_overlay')
    var delete_overlay = document.getElementById('delete_overlay')
    var assign_overlay = document.getElementById("assign_overlay")
    if (event.target == overlay_share) {
        closeShare();
    }
    if (event.target == overlay_display) {
        closeBranching();
    }
    if (event.target == delete_overlay) {
        closeDelete();
    }
    if (event.target == assign_overlay) {
        closeAssign();
    }
}


// EVERYTHING FROM HERE TO THE window.addEventListener('beforeunload') IS THE BRANCHING SECTION 

var id = document.getElementById("drawflow");
const editor = new Drawflow(id);
editor.reroute = true;

//variable related to the zoom in and out of the drawflow
editor.zoom_max = 2;
editor.zoom_min = 0.2;
editor.zoom_value = 0.1;

editor.draggable_inputs = false;
editor.start();

editor.editor_mode = 'edit';

let drawflowSnapshot = null;
let drawflowDirty = false;

const deletedQuestionIds = new Set();
const nodeQuestionMap = {};

/**
 * Allow for zooming in and out of the drawflow with the wheel of their mouse
 */
document.getElementById('drawflow').addEventListener('wheel', function (e) {
    e.preventDefault();
    if (e.deltaY < 0) {
        editor.zoom_in();
    } else {
        editor.zoom_out();
    }
}, { passive: false });


/**
 * Template for the multiple choice question.
*/
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

/**
 * Template for the result/pure text section.
*/
const endTemplate = `
    <div class="end-node">
        <input class="end-title drawflow-input" type="text" placeholder="Title" oninput="updateResultText(this)"/>
        <textarea class="end-body drawflow-input" placeholder="Body (optional)" oninput="updateResultBody(this)"></textarea>
        <label class="email-append-label">
            <input type="checkbox" class="email-append-checkbox drawflow-input" onchange="updateEmailAppendToggle(this)">
            Append to email?
        </label>
        <textarea class="email-text drawflow-input" placeholder="Text to append to email (optional)" style="display:none" oninput="updateEmailAppendText(this)"></textarea>
    </div>
`;

/**
 * Template for the free answer question.
*/
const freeResponseTemplate = `
    <div class="freeresponse-node">
        <input class="fr-title drawflow-input" type="text" placeholder="Question text" oninput="updateFreeResponseText(this)"/>
    </div>
`;

/**
 * Get the quiz question object associated with a drawflow node
 * @param {*} nodeId the id of the drawflow node
 * @returns the question object from quiz, or null if not found
 */
function getQuizQuestion(nodeId) {
    const node = editor.getNodeFromId(nodeId);
    const allQuestions = quiz.categories.flatMap(cat => cat.items);
    return allQuestions.find(q => q.id === node.data.question_id) || null;
}


/**
 * Add an answer option to a question in the drawflow editor
 * @param {*} btn the button that was clicked
 */
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

/**
 * Remove an answer option from a question node in the drawflow editor
 * Also removes the corresponding output and any connections attached to it
 * @param {*} btn the button that was clicked
 * @returns here to break out of the function if only one answer remains
 */
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


/**
 * Allow the node type elements in the sidebar to be dragged onto the drawflow canvas.
 */
document.querySelectorAll('.node-type').forEach(el => {
    el.addEventListener('dragstart', e => {
        e.dataTransfer.setData('node-type', e.target.dataset.node);
    });
});

/**
 * Allow the drawflow canvas to receive dropped elements by preventing the default, browser behavior (which would otherwise reject the drop).
*/
document.getElementById('drawflow').addEventListener('dragover', e => e.preventDefault());

/**
 * Handle a node being dropped onto the drawflow canvas.
 */
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
    } else if (type == 'result') {
        editor.addNode('result', 1, 1, pos_x, pos_y, 'result', {}, endTemplate);
    } else if (type == 'freeresponse') {
        editor.addNode('freeresponse', 1, 1, pos_x, pos_y, 'freeresponse', {}, freeResponseTemplate);
    }
});

/**
 * Enforces a maximum of one connection per output (removes the old one if a second is drawn),
 */
editor.on('connectionCreated', function (info) {
    drawflowDirty = true;
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
        // prevent leadsto from being automatically generated in the future
        question.answer[answerIndex].auto_leads_to = false;
    }

    const allQuestions = quiz.categories.flatMap(cat => cat.items);
    const target = allQuestions.find(q => q.id === targetNode.data.question_id);
    const indicators = document.querySelectorAll('#answer_panel .answer-leadsto-indicator');
    if (indicators[answerIndex])
        indicators[answerIndex].textContent = target ? `⇒ ${target.text || '(unnamed)'}` : '';
});
/**
 * Fired by drawflow when a connection between two nodes is removed.Clears the inputConnected style on the target node if it has no remaining connections,
 */
editor.on("connectionRemoved", function (info) {
    drawflowDirty = true;
    const node = editor.getNodeFromId(info.input_id);
    const connections = node.inputs[info.input_class].connections;

    if (connections.length === 0) {
        document.getElementById('node-' + info.input_id).getElementsByClassName(info.input_class)[0].classList.remove('inputConnected');
    }

    const answerIndex = parseInt(info.output_class.replace('output_', '')) - 1;
    const question = getQuizQuestion(info.output_id);
    if (question?.answer[answerIndex]) {
        question.answer[answerIndex].leads_to = null;
        question.answer[answerIndex].auto_leads_to = true;
    }

    const indicators = document.querySelectorAll('#answer_panel .answer-leadsto-indicator');
    if (indicators[answerIndex])
        indicators[answerIndex].textContent = "";
});

/**
 * Fired by drawflow when a node is deleted from the canvas.Removes the corresponding question from quiz.categories, as well as any dependency that question had
 */
editor.on('nodeRemoved', function (nodeId) {
    const question_id = nodeQuestionMap[nodeId];
    if (question_id) {
        // Immediately purge from data model
        quiz.categories.forEach(cat => {
            cat.items = cat.items.filter(q => q.id !== question_id);
        });
        // Null out any leads_to references pointing to the deleted question
        quiz.categories.forEach(cat => {
            cat.items.forEach(q => {
                (q.answer || []).forEach(a => {
                    if (a.leads_to === question_id) a.leads_to = null;
                });
            });
        });

        deletedQuestionIds.add(question_id); // keep as safety net
        delete nodeQuestionMap[nodeId];
        markDirty();
    }
});



/**
 * Renumber the placeholder text of all answer inputs inside a question. Called after adding or removing an answer to keep labels consistent
 * @param {*} nodeEl the node containing the answers
 */
function renumberAnswers(nodeEl) {
    const answers = nodeEl.querySelectorAll('.answer input');
    answers.forEach((input, i) => {
        input.placeholder = `Option ${i + 1}`;
    });
}

/**
 * Compute an auto-layout position for each question node based on the branching graph.
 * Nodes are placed in layers (left to right) determined by their longest path from a root node.
 * @param {*} allQuestions flat array of all question objects across all categories
 * @returns a dictionary mapping question id to {x, y} position
 */
function computeAutoLayout(allQuestions) {
    const idToQ = {};
    allQuestions.forEach(q => idToQ[q.id] = q);


    const outgoing = {};
    const incoming = {};
    allQuestions.forEach(q => { outgoing[q.id] = []; incoming[q.id] = []; });

    allQuestions.forEach(q => {
        (q.answer || []).forEach(a => {
            if (a.leads_to && idToQ[a.leads_to]) {
                outgoing[q.id].push(a.leads_to);
                incoming[a.leads_to].push(q.id);
            }
        });
    });


    const layer = {};
    const roots = allQuestions.filter(q => incoming[q.id].length === 0).map(q => q.id);
    const startNodes = roots.length ? roots : [allQuestions[0]?.id].filter(Boolean);

    startNodes.forEach(id => layer[id] = 0);


    let changed = true;
    let iterations = 0;
    const maxIterations = allQuestions.length + 5;
    while (changed && iterations < maxIterations) {
        changed = false;
        iterations++;
        allQuestions.forEach(q => {
            if (layer[q.id] === undefined) return;
            outgoing[q.id].forEach(targetId => {
                const candidate = layer[q.id] + 1;
                if (layer[targetId] === undefined || candidate > layer[targetId]) {

                    if (candidate <= allQuestions.length) {
                        layer[targetId] = candidate;
                        changed = true;
                    }
                }
            });
        });
    }


    allQuestions.forEach(q => { if (layer[q.id] === undefined) layer[q.id] = 0; });


    const layers = {};
    allQuestions.forEach((q, i) => {
        const l = layer[q.id];
        if (!layers[l])
            layers[l] = [];
        layers[l].push(q.id);
    });

    //A spacing of (450,280) usually give a good spacing (at least on my testing part)
    const positions = {};
    const X_SPACING = 450;
    const Y_SPACING = 280;
    const X_OFFSET = 50;
    const Y_OFFSET = 50;

    const layerKeys = Object.keys(layers).map(Number).sort((a, b) => a - b);

    layerKeys.forEach(l => {
        let ids = layers[l];

        if (l > 0) {
            ids = ids.slice().sort((a, b) => {
                const avgY = id => {
                    const sources = incoming[id];
                    if (!sources.length)
                        return Infinity;
                    const ys = sources
                        .filter(s => positions[s] !== undefined)
                        .map(s => positions[s].y);
                    if (!ys.length)
                        return Infinity;
                    return ys.reduce((sum, v) => sum + v, 0) / ys.length;
                };
                return avgY(a) - avgY(b);
            });
        }

        ids.forEach((id, idx) => {
            positions[id] = {
                x: X_OFFSET + l * X_SPACING,
                y: Y_OFFSET + idx * Y_SPACING
            };
        });
    });

    return positions;
}


/**
 * Load the current quiz into the drawflow editor, creating one node per question, and drawing connections based on each answer's leads_to value.
 * Only called once when the branching overlay is first opened.
 */
function loadQuizIntoDrawflow() {
    editor.clearModuleSelected();

    const allQuestions = quiz.categories.flatMap(cat => cat.items);
    const nodeIds = [];
    const positions = computeAutoLayout(allQuestions);


    allQuestions.forEach((q, i) => {
        const { x, y } = positions[q.id] || { x: i * 350 + 50, y: 200 };

        let nodeId;

        if (q.type == 'result') {
            const emailChecked = q['email-append'] ? 'checked' : '';
            const emailDisplay = q['email-append'] ? 'block' : 'none';
            const template = `
        <div class="end-node">
            <input class="end-title drawflow-input" type="text" placeholder="Title" value="${q.text || ''}" oninput="updateResultText(this)"/>
            <textarea class="end-body drawflow-input" placeholder="Body (optional)" oninput="updateResultBody(this)">${q.result_body || ''}</textarea>
            <label class="email-append-label">
                <input type="checkbox" class="email-append-checkbox drawflow-input" ${emailChecked} onchange="updateEmailAppendToggle(this)">
                Append to email?
            </label>
            <textarea class="email-text drawflow-input" placeholder="Text to append to email (optional)" style="display:${emailDisplay}" oninput="updateEmailAppendText(this)">${q['email-append-text'] || ''}</textarea>
         </div>`;
            nodeId = editor.addNode('result', 1, 1, x, y, 'result', { question_id: q.id }, template);
            nodeQuestionMap[nodeId] = q.id;
        } else if (q.type == 'text') {
            const template = `
            <div class="freeresponse-node">
                <input class="fr-title drawflow-input" type="text" placeholder="Question text" value="${q.text || ''}" oninput="updateFreeResponseText(this)"/>
            </div>`;
            nodeId = editor.addNode('freeresponse', 1, 1, x, y, 'freeresponse', { question_id: q.id }, template);
            nodeQuestionMap[nodeId] = q.id;
        } else {
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
            nodeId = editor.addNode('question', 1, numOutputs, x, y, 'question', { question_id: q.id }, template);
            nodeQuestionMap[nodeId] = q.id;
        }

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
                }
            });
        }); drawflowDirty = false;
    }, 100);
}

/**
 * Fired by drawflow whenever a new node is dropped onto the canvas. Creates the corresponding
 * question object in quiz.categories (result, free response, or multiple choice depending on
 * the node's type), links it back to that question via nodeQuestionMap, and (for question nodes)
 * rebuilds the node's inner HTML so its inputs are wired up to the update functions.
 * @param {*} nodeId the id of the newly created drawflow node
 */
editor.on('nodeCreated', function (nodeId) {
    const node = editor.getNodeFromId(nodeId);

    if (node.name === 'result') {
        if (node.data.question_id) return;

        const q_id = uid();
        const newQuestion = {
            id: q_id, text: '', result_body: '', type: 'result', answer: [{ id: uid(), text: '', leads_to: null }]
        };

        editor.drawflow.drawflow.Home.data[nodeId].data.question_id = q_id;
        nodeQuestionMap[nodeId] = q_id;
        quiz.categories[0].items.push(newQuestion);
        return;
    }

    if (node.name === 'freeresponse') {
        if (node.data.question_id) return;
        const q_id = uid();
        const newQuestion = {
            id: q_id, text: '', type: 'text', answer: [{ id: uid(), text: '', leads_to: null }]
        };
        editor.drawflow.drawflow.Home.data[nodeId].data.question_id = q_id;
        nodeQuestionMap[nodeId] = q_id;
        quiz.categories[0].items.push(newQuestion);
        return;
    }

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
    nodeQuestionMap[nodeId] = q_id;
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


/**
 * Update the text of a free response question when its node input changes
 * @param {*} input the input element inside the freeresponse node
 */
function updateFreeResponseText(input) {
    drawflowDirty = true;
    const nodeEl = input.closest('.drawflow-node');
    const nodeId = nodeEl.id.replace('node-', '');
    const question = getQuizQuestion(nodeId);
    if (question) question.text = input.value;
}

/**
 * Update the text of a multiple choice question when its node input changes
 * @param {*} input the input element inside the question node
 */
function updateQuestionText(input) {
    drawflowDirty = true;
    const nodeEl = input.closest('.drawflow-node');
    const nodeId = nodeEl.id.replace('node-', '');
    const question = getQuizQuestion(nodeId);
    if (question) question.text = input.value;
}

/**
 * Update the text of a specific answer option when its node input changes
 * @param {*} input the input element inside the answer row
 */
function updateAnswerText(input) {
    drawflowDirty = true;
    const nodeEl = input.closest('.drawflow-node');
    const nodeId = nodeEl.id.replace('node-', '');
    const question = getQuizQuestion(nodeId);
    if (!question) return;

    const answerEl = input.closest('.answer');
    const outputKey = answerEl.dataset.output;
    const answerIndex = parseInt(outputKey.replace('output_', '')) - 1;
    if (question.answer[answerIndex]) question.answer[answerIndex].text = input.value;
}

/**
 * Update the title text of a result node when its input changes
 * @param {*} input the input element inside the result node
 */
function updateResultText(input) {
    drawflowDirty = true;
    const nodeEl = input.closest('.drawflow-node');
    const nodeId = nodeEl.id.replace('node-', '');
    const question = getQuizQuestion(nodeId);
    if (question) question.text = input.value;
}

/**
 * Update the body text of a result node when its textarea changes
 * @param {*} input the textarea element inside the result node
 */
function updateResultBody(input) {
    drawflowDirty = true;
    const nodeEl = input.closest('.drawflow-node');
    const nodeId = nodeEl.id.replace('node-', '');
    const question = getQuizQuestion(nodeId);
    if (question) question.result_body = input.value;
}

function updateEmailAppendToggle(checkbox) {
    drawflowDirty = true;
    const nodeEl = checkbox.closest('.drawflow-node');
    const nodeId = nodeEl.id.replace('node-', '');
    const question = getQuizQuestion(nodeId);
    if (question) question['email-append'] = checkbox.checked;

    const textarea = nodeEl.querySelector('.email-text');
    if (textarea) textarea.style.display = checkbox.checked ? 'block' : 'none';
}

function updateEmailAppendText(input) {
    drawflowDirty = true;
    const nodeEl = input.closest('.drawflow-node');
    const nodeId = nodeEl.id.replace('node-', '');
    const question = getQuizQuestion(nodeId);
    if (question) question['email-append-text'] = input.value;
}


/**
 * read every node's current DOM state and write to quiz
 */
function saveDrawflowChanges() {

    const allNodes = editor.export().drawflow.Home.data;

    for (const nodeId in allNodes) {
        const node = allNodes[nodeId];
        const question = getQuizQuestion(nodeId);
        if (!question) continue;

        const nodeEl = document.querySelector(`#node-${nodeId} .drawflow_content_node`);
        if (!nodeEl) continue;

        if (node.name === 'question') {
            const titleInput = nodeEl.querySelector('.question-title');
            if (titleInput) question.text = titleInput.value;

            const answerInputs = nodeEl.querySelectorAll('.answer input');
            answerInputs.forEach((input, i) => {
                if (question.answer[i]) question.answer[i].text = input.value;
            });
        } else if (node.name === 'result') {
            const titleInput = nodeEl.querySelector('.end-title');
            const bodyInput = nodeEl.querySelector('.end-body');
            const emailCheckbox = nodeEl.querySelector('.email-append-checkbox');
            const emailTextarea = nodeEl.querySelector('.email-text');
            if (titleInput) question.text = titleInput.value;
            if (bodyInput) question.result_body = bodyInput.value;
            if (emailCheckbox) question['email-append'] = emailCheckbox.checked;
            if (emailTextarea) question['email-append-text'] = emailTextarea.value;
        }
    }
    if (deletedQuestionIds.size > 0) {
        quiz.categories.forEach(cat => {
            cat.items = cat.items.filter(q => !deletedQuestionIds.has(q.id));
        });
        quiz.categories.forEach(cat => {
            cat.items.forEach(q => {
                (q.answer || []).forEach(a => {
                    if (deletedQuestionIds.has(a.leads_to)) a.leads_to = null;
                });
            });
        });
        deletedQuestionIds.clear();
    }

    drawflowSnapshot = null;
    markDirty();

    // refresh regular editor
    render();

    if (active_question_Id && active_category_Id) {
        renderAnswerPanel(active_category_Id, active_question_Id);
    } else {
        closeAnswerPanel();
    }
    if (active_category_Id) {
        renderQuestions(active_category_Id);
    }

    document.getElementById('branching_overlay').style.display = 'none';
    saveQuiz();
}

/**
 * Here to prevent a user from leaving the page if any change has been made.
 */
window.addEventListener('beforeunload', (event) => {
    if (isDirty) {
        event.preventDefault();
        event.returnValue = '';
    }
});


// having render here ensure that everything is shown properly, as it will render everything once when the page is loaded for the first time
render();