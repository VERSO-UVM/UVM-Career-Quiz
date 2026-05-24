var id = document.getElementById("drawflow");
const editor = new Drawflow(id);
editor.reroute = true;
editor.start();
editor.editor_mode = 'edit';

function questionTemplate() {
    return `
    <div class="question-node">
      <input class="question-title" type="text" placeholder="Question text" />
      <div class="answers">
        <div class="answer" data-output="output_1">
          <input type="text" placeholder="Option 1" />
          <button class="remove-answer" onclick="removeAnswer(this)">-</button>
        </div>
        <div class="answer" data-output="output_2">
          <input type="text" placeholder="Option 2" />
          <button class="remove-answer" onclick="removeAnswer(this)">-</button>
        </div>
      </div>
      <button class="add-answer" onclick="addAnswer(this)">+</button>
    </div>
  `;
}

function endTemplate() {
    return `
    <div class="end-node">
      <input class="end-title" type="text" placeholder="Result" />
    </div>
  `;
}

function addAnswer(btn) {
    const answers = btn.previousElementSibling;
    const nodeEl = btn.closest('.drawflow-node');
    const nodeId = nodeEl.id.replace('node-', '');

    const outputKey = addOutputToNode(nodeId);

    const div = document.createElement('div');
    div.classList.add('answer');
    div.dataset.output = outputKey;
    div.innerHTML = `
        <input type="text" placeholder="Option" />
        <button class="remove-answer" onclick="removeAnswer(this)">-</button>`;
    answers.appendChild(div);

    renumberAnswers(nodeEl);
}

function removeAnswer(btn) {
    const answer = btn.parentElement;
    const nodeEl = btn.closest('.drawflow-node');
    const nodeId = nodeEl.id.replace('node-', '');

    const answers = answer.parentElement;
    if (answers.children.length <= 1) return;

    const outputKey = answer.dataset.output;
    removeOutputFromNode(nodeId, outputKey);
    answer.remove();
    renumberAnswers(nodeEl);
}

function removeOutputFromNode(nodeId, outputKey) {
    const node = editor.getNodeFromId(nodeId);

    // remove connections first
    const connections = [...(node.outputs[outputKey]?.connections || [])];
    connections.forEach(conn => {
        editor.removeSingleConnection(nodeId, conn.node, outputKey, conn.output);
    });

    // remove the DOM circle
    const outputEl = document.querySelector(`#node-${nodeId} .outputs .${outputKey}`);
    if (outputEl) outputEl.remove();

    delete node.outputs[outputKey];

    updateAllConnections();
}

function addOutputToNode(nodeId) {
    const node = editor.getNodeFromId(nodeId);
    const outputKeys = Object.keys(node.outputs);
    const maxNum = outputKeys.reduce((max, key) => {
        const num = parseInt(key.replace('output_', ''));
        return num > max ? num : max;
    }, 0);
    const outputKey = `output_${maxNum + 1}`;
    editor.addNodeOutput(nodeId);

    updateAllConnections();
    return outputKey;
}

function updateAllConnections() {
    // delay so it has a chance to update!
    setTimeout(() => {
        const data = editor.export();
        Object.keys(data.drawflow.Home.data).forEach(nodeId => {
            editor.updateConnectionNodes(`node-${nodeId}`);
        });
    }, 10);
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
        editor.addNode('question', 1, 2, pos_x, pos_y, 'question', {}, questionTemplate());
    } else if (type == 'end') {
        editor.addNode('end', 1, 0, pos_x, pos_y, 'end', {}, endTemplate());
    }
});

editor.on('connectionCreated', function (info) {
    const node = editor.getNodeFromId(info.output_id);
    const connections = node.outputs[info.output_class].connections; // was .info

    if (connections.length > 1) {
        const old = connections[0];
        editor.removeSingleConnection(info.output_id, old.node, info.output_class, old.output);
    }

    document.getElementById('node-' + info.input_id).getElementsByClassName(info.input_class)[0].classList.add('inputConnected');
});

editor.on("connectionRemoved", function (info) {
    const node = editor.getNodeFromId(info.input_id);
    const connections = node.inputs[info.input_class].connections; // was outputs, and .info

    if (connections.length === 0) {
        document.getElementById('node-' + info.input_id).getElementsByClassName(info.input_class)[0].classList.remove('inputConnected');
    }
});

function renumberAnswers(nodeEl) {
    const answers = nodeEl.querySelectorAll('.answer input');
    answers.forEach((input, i) => {
        input.placeholder = `Option ${i + 1}`;
    });
}
