function uid() {
    return Math.random().toString(36).slice(2, 9);
}

let quiz = {
    title: '',
    desc: '',
    categories: []
};

function addBlock() {
    const id = uid();
    quiz.categories.push({ id, name: '', items: [] });
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
function render() {
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