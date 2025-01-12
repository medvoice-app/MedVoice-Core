document.getElementById('uploadAudioForm').addEventListener('submit', function(e) {
    e.preventDefault();
    handleAudioUpload();
});

async function handleAudioUpload() {
    const userId = document.getElementById('audioUserId').value;
    const fileInput = document.getElementById('audioFile');
    const statusDiv = document.getElementById('uploadStatus');
    const spinner = document.getElementById('audioUploadSpinner');

    if (!validateInput(userId, fileInput, statusDiv)) return;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        statusDiv.innerHTML = ''; // Clear any previous status
        spinner.style.display = 'block'; // Show spinner
        const data = await uploadAudio(userId, formData);
        handleUploadSuccess(data, statusDiv);
        createTaskRow(data, 'audioTaskTable');
    } catch (error) {
        updateStatus(statusDiv, `Error: ${error.message}`, 'red');
    } finally {
        spinner.style.display = 'none'; // Hide spinner
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
    
    const data = await response.json();
    return data;
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
