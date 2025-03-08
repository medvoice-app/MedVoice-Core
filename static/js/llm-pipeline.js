document.getElementById('audioForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const userId = document.getElementById('userId').value;
    const params = new URLSearchParams({
        file_id: document.getElementById('fileId').value,
        file_extension: document.getElementById('fileExtension').value,
        file_name: document.getElementById('fileName').value
    }).toString();

    const url = `${apiUrl}process_audio_v2/${userId}?${params}`;
    processAudioRequest(url);
});

// Update the original usage in llm-pipeline.js
async function processAudioRequest(url) {
    try {
        const response = await fetch(url, { method: 'POST' });
        const data = await response.json();
        createTaskRow(data, 'taskTable');  // Explicitly specify default table
    } catch (error) {
        console.error('Error processing audio:', error);
        alert('An error occurred while processing the audio.');
    }
}

// Updated to accept tableId parameter
function createTaskRow(data, tableId = 'taskTable') {
    const table = document.getElementById(tableId);
    if (!table) {
        console.error(`Table with ID ${tableId} not found`);
        return;
    }

    const tbody = table.getElementsByTagName('tbody')[0];
    if (!tbody) {
        console.error(`No tbody found in table ${tableId}`);
        return;
    }

    const tr = document.createElement('tr');
    const td1 = document.createElement('td');
    const td2 = document.createElement('td');

    td1.textContent = data.task_id;
    td1.className = "border px-6 py-4";

    td2.className = "border px-6 py-4";

    const checkStatusButton = createCheckStatusButton(data.task_id);
    td2.appendChild(checkStatusButton);

    tr.appendChild(td1);
    tr.appendChild(td2);
    tbody.appendChild(tr);
}

function createCheckStatusButton(taskId) {
    const button = document.createElement('button');
    button.textContent = 'Check Status';
    button.className = "status-button";  // Use our custom class

    button.addEventListener('click', () => checkTaskStatus(taskId, button));

    return button;
}

async function checkTaskStatus(taskId, button) {
    try {
        const response = await fetch(`${apiUrl}get_audio_task/${taskId}`);
        const data = await response.json();

        if (data.status === 'SUCCESS') {
            handleSuccessStatus(data, button);
        } else {
            alert('Task Status: ' + data.status);
        }
    } catch (error) {
        console.error('Error fetching task result:', error);
        alert('An error occurred. Please try again.');
    }
}

function handleSuccessStatus(data, button) {
    button.textContent = 'Done';
    createJsonModal(data.llama3_json_output);
}

function createJsonModal(jsonData) {
    const modal = createModalStructure();
    const modalContent = createModalContent();
    const closeButton = createCloseButton(modal);
    const table = createJsonTable(jsonData);
    const viewAsTextBtn = createViewAsTextButton(jsonData, table);

    modalContent.appendChild(closeButton);
    modalContent.appendChild(table);
    modalContent.appendChild(viewAsTextBtn);
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
}

// Helper functions for modal creation
function createModalStructure() {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full';
    modal.id = 'jsonModal';
    return modal;
}

function createModalContent() {
    const modalContent = document.createElement('div');
    modalContent.className = 'relative top-20 mx-auto p-5 border w-4/5 shadow-lg rounded-md bg-white';
    return modalContent;
}

function createCloseButton(modal) {
    const closeButton = document.createElement('button');
    closeButton.innerHTML = '×';
    closeButton.className = 'absolute right-2 top-2 text-gray-600 text-2xl font-bold hover:text-gray-900';
    closeButton.onclick = () => modal.remove();
    return closeButton;
}

function createJsonTable(jsonData) {
    const table = document.createElement('table');
    table.className = 'min-w-full bg-white border border-gray-300';
    createTableFromJSON(jsonData, table.createTBody());
    return table;
}

function createTableFromJSON(obj, parent, indent = 0) {
    for (let key in obj) {
        const tr = document.createElement('tr');
        const tdKey = document.createElement('td');
        const tdValue = document.createElement('td');

        tdKey.className = 'px-4 py-2 border border-gray-300 font-semibold';
        tdValue.className = 'px-4 py-2 border border-gray-300';

        tdKey.style.paddingLeft = `${indent * 20}px`;
        tdKey.textContent = key;

        if (typeof obj[key] === 'object' && obj[key] !== null) {
            parent.appendChild(tr);
            tr.appendChild(tdKey);
            tr.appendChild(tdValue);
            createTableFromJSON(obj[key], parent, indent + 1);
        } else {
            tdValue.textContent = obj[key];
            parent.appendChild(tr);
            tr.appendChild(tdKey);
            tr.appendChild(tdValue);
        }
    }
}

function createViewAsTextButton(jsonData, table) {
    const viewAsTextBtn = document.createElement('button');
    viewAsTextBtn.textContent = 'View as Text';
    viewAsTextBtn.className = 'json-button';  // Use our custom class

    viewAsTextBtn.onclick = () => {
        const formattedText = JSON.stringify(jsonData, null, 2);
        const textArea = document.createElement('textarea');
        textArea.value = formattedText;
        textArea.className = 'w-full h-96 mt-4 p-2 font-mono text-sm border rounded';
        textArea.readOnly = true;

        table.replaceWith(textArea);
        viewAsTextBtn.textContent = 'View as Table';
        viewAsTextBtn.onclick = () => {
            textArea.replaceWith(table);
            viewAsTextBtn.textContent = 'View as Text';
            viewAsTextBtn.onclick = () => viewAsTextBtn.click();
        };
    };

    return viewAsTextBtn;
}

