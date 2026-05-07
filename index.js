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
    quiz.categories.push({ id, name: 'New Block', items: [] });
    activeCatId = id;
    render();
    console.log(quiz)
}

function render() {
    const container = document.getElementById('block');
    container.innerHTML = quiz.categories.map(cat => {
    return `${cat.id}`

    });
}