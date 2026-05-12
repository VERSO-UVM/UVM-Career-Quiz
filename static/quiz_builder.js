function uid() {
    return Math.random().toString(36).slice(2, 9);
}

let quiz = {
    title: '',
    desc: '',
    categories: []
};

let active_category_Id = null;

function getQuizInfo() {
    quiz.title = document.getElementById('quiz-title').value;
    quiz.desc = document.getElementById('quiz-desc').value;
}

function addBlock() {
    const id = uid();
    /* 25 is an arbitrary number for the sake of having a limit, might want to remove that one day */
    if (quiz.categories.length >= 25) {
        alert("Too many categories");
        return;
    }
    quiz.categories.push({ id, name: 'Block ' + (quiz.categories.length + 1), items: [] });
    render();
}

function changeBlockName(id, new_name) {
    const category = quiz.categories.find(block => block.id === id);
    if (category) {
        category.name = new_name;
        if (active_category_Id === id) {
            document.getElementById('editor_block_title').textContent = new_name;
        }
    }
}

function removeBlock(id) {
    quiz.categories = quiz.categories.filter(block => block.id !== id);

    // Renumber blocks that still have default names
    quiz.categories.forEach((block, index) => {
        if (/^Block \d+$/.test(block.name)) {
            block.name = 'Block ' + (index + 1);
        }
    });

    // If the removed block was active, close the editor
    if (active_category_Id === id) {
        active_category_Id = null;
        closeEditor();
    }

    render();
}

function openEditor(id) {
    active_category_Id = id;
    const category = quiz.categories.find(b => b.id === id);
    if (!category) return;

    document.getElementById('question_editor').style.display = 'flex';
    document.getElementById('empty_state').style.display = 'none';
    document.getElementById('editor_block_title').textContent = category.name;

    renderQuestions(id);

    // Highlight active block in sidebar
    document.querySelectorAll('.block_item').forEach(el => el.classList.remove('active'));
    const activeEl = document.querySelector(`.block_item[data-id="${id}"]`);
    if (activeEl) activeEl.classList.add('active');
}

function closeEditor() {
    document.getElementById('question_editor').style.display = 'none';
    document.getElementById('empty_state').style.display = 'flex';
    document.querySelectorAll('.block_item').forEach(el => el.classList.remove('active'));
    active_category_Id = null;
}

function addQuestion(cat_Id) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category) return;
    const q_Id = uid();
    category.items.push({ id: q_Id, text: '', type: 'text' });
    renderQuestions(cat_Id);
}

function removeQuestion(cat_Id, q_Id) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category) return;
    category.items = category.items.filter(q => q.id !== q_Id);
    renderQuestions(cat_Id);
}

function changeQuestionText(cat_Id, q_Id, new_Text) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category)
        return;
    const question = category.items.find(q => q.id === q_Id);
    if (question)
        question.text = new_Text;
}

function renderQuestions(cat_Id) {
    const category = quiz.categories.find(b => b.id === cat_Id);
    if (!category)
        return;

    const container = document.getElementById('questions_list');
    if (!category.items.length) {
        container.innerHTML = `<p class="no_questions">No questions yet. Add one below.</p>`;
        return;
    }

    container.innerHTML = category.items.map((q, index) => `
        <div class="question_item" id="q_${q.id}">
            <span class="question_number">Q${index + 1}</span>
            <input
                class="question_input"
                value="${q.text.replace(/"/g, '&quot;')}"
                placeholder="Type your question here…"
                oninput="changeQuestionText('${cat_Id}', '${q.id}', this.value)"
            />
            <button class="remove_question" onclick="removeQuestion('${cat_Id}', '${q.id}')">✕</button>
        </div>
    `).join('');
}

function renderBlock() {
    const container = document.getElementById('block');
    container.innerHTML = quiz.categories.map((block, index) => `
        <div class="block_item${active_category_Id === block.id ? ' active' : ''}" data-id="${block.id}" onclick="openEditor('${block.id}')">
            <span class="block_number">${index + 1}</span>
            <input
                class="block_name_input"
                value="${block.name.replace(/"/g, '&quot;')}"
                oninput="changeBlockName('${block.id}', this.value)"
                onclick="event.stopPropagation()"
                placeholder="Block name"
            />
            <button class="remove_block" onclick="event.stopPropagation(); removeBlock('${block.id}')">✕</button>
        </div>
    `).join('');
}

/**
 * Broke off render into multiple functions in order to avoid cluttering, and for an easier experience reading the code
 */
function render() {
    getQuizInfo();
    renderBlock();
}

function saveQuiz() {
    if (!quiz.title)
        alert("You have not chosen the name of your quiz. Please do so before saving it")
        return 
    const jsonString = JSON.stringify(quiz, null, 2);

    fetch('/save-quiz', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: jsonString
    })
}

function loadQuiz() {
    // TODO implement this function. Ideally what it would do is fetch a specific quiz via the flask backend. 
}