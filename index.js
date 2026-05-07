
/**
 * Gives us a random id for every function
 */
function uid() {
    return Math.random().toString(36).slice(2, 9);
}

let quiz = {
    title: '',
    desc: '',
    categories: []
};

function getQuizInfo() {
  quiz.title = document.getElementById('quiz-title').value;
  quiz.desc = document.getElementById('quiz-desc').value;
}
function addBlock() {
    const id = uid();
    /* 25 is an arbitrary number for the sake of having a limit  */
    if(quiz.categories.length >= 25){
        alert("Too many category")
        return 
    }
    /* will have to refactor the naming system. As of right now doesnt take into account deletion */
    quiz.categories.push({ id, name: 'New Block ' + (quiz.categories.length + 1), items: [] });
    activeCatId = id;
    render();
}

function changeBlockName(id, newName) {
    const category = quiz.categories.find(block => block.id === id);
    category.name = newName;
}

function removeBlock(id) {
    quiz.categories = quiz.categories.filter(block => block.id !== id);
    render();
}

/**
 * Broke off render into multiple function in order to avoid clutering, and for an easier experience reading the code
 */
function renderBlock(){
        const container = document.getElementById('block');
    container.innerHTML = quiz.categories.map(block => {
        return `<div id="${block.id}">
                        <input id = "${block.id}" class="block_name_input" value="${block.name}" 
                        oninput="changeBlockName('${block.id}', this.value)"
                        placeholder="Block name">
                    <button class="remove_block" onclick="removeBlock('${block.id}')">✕</button>
                </div>`;
    }).join('');
}

/**
 * Eventually will have every single thing we want to render on the page in this function 
 */
function render() {
    getQuizInfo()
    renderBlock()
    console.log(quiz)
}