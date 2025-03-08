document.getElementById('uploadAudioForm').addEventListener('submit', function (e) {
    e.preventDefault();
    handleAudioUpload();
});

async function handleAudioUpload() {
    const userId = document.getElementById('audioUserId').value;
    const fileInput = document.getElementById('audioFile');
    const statusDiv = document.getElementById('uploadStatus');

    if (!validateInput(userId, fileInput, statusDiv)) return;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        updateStatus(statusDiv, 'Uploading and processing...', 'blue');
        const data = await uploadAudio(userId, formData);
        handleUploadSuccess(data, statusDiv);
        createTaskRow(data);
    } catch (error) {
        updateStatus(statusDiv, `Error: ${error.message}`, 'red');
    }
}

function validateInput(userId, fileInput, statusDiv) {
    if (!userId) {
        updateStatus(statusDiv, 'Please enter a User ID', 'red');
        return false;
    }
    if (!fileInput.files[0]) {
        updateStatus(statusDiv, 'Please select an audio file', 'red');
        return false;
    }
    return true;
}

async function uploadAudio(userId, formData) {
    const response = await fetch(`${apiUrl}process_upload_audio/${userId}`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const errorText = await response.text();
        try {
            const errorJson = JSON.parse(errorText);
            throw new Error(errorJson.detail || 'Upload failed');
        } catch (e) {
            throw new Error(errorText || 'Upload failed');
        }
    }

    return await response.json();
}

function updateStatus(statusDiv, message, color) {
    statusDiv.innerHTML = `<p class="text-${color}-500">${message}</p>`;
}

function handleUploadSuccess(data, statusDiv) {
    const taskId = data.task_id || 'N/A';
    const filename = data.filename || 'Unknown file';

    statusDiv.innerHTML = `
        <p class="text-green-500">Upload successful!</p>
        <p>Task ID: ${taskId}</p>
        <p>Filename: ${filename}</p>
    `;
}

function createTaskRow(data) {
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
    document.getElementById('audioTaskTable').getElementsByTagName('tbody')[0].appendChild(tr);
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
            button.textContent = 'Done';
            alert('Audio processing completed successfully!');
        } else {
            alert('Task Status: ' + data.status);
        }
    } catch (error) {
        console.error('Error checking task status:', error);
        alert('An error occurred while checking the status.');
    }
}
