/**
 * Fetch JSON transcripts for a specific user
 */
async function fetchTranscriptsByUser(userId) {
    const spinner = document.getElementById('transcript-spinner');
    const errorContainer = document.getElementById('transcript-error');
    const resultsContainer = document.getElementById('transcript-results');

    try {
        // Show spinner
        spinner.style.display = 'block';
        errorContainer.style.display = 'none';
        resultsContainer.innerHTML = '';

        // Fetch transcripts
        const response = await fetch(`${apiUrl}get_json_transcripts_by_user/${userId}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Display transcripts
        if (data.patients && data.patients.length > 0) {
            // Add view toggle buttons
            addViewToggleButtons(resultsContainer);
            displayTranscripts(data.patients);
        } else {
            resultsContainer.innerHTML = '<p class="text-gray-500 text-center p-4">No transcripts found for this user.</p>';
        }
    } catch (error) {
        console.error('Error fetching transcripts:', error);
        errorContainer.textContent = `Error: ${error.message}`;
        errorContainer.style.display = 'block';
    } finally {
        // Hide spinner
        spinner.style.display = 'none';
    }
}

/**
 * Add toggle buttons for different view modes
 */
function addViewToggleButtons(container) {
    const toggleContainer = document.createElement('div');
    toggleContainer.className = 'flex justify-end mb-4';

    const cardViewBtn = document.createElement('button');
    cardViewBtn.textContent = 'Card View';
    cardViewBtn.className = 'bg-blue-600 text-white px-4 py-2 rounded-l-md';
    cardViewBtn.id = 'card-view-btn';
    cardViewBtn.onclick = () => switchView('card');

    const tableViewBtn = document.createElement('button');
    tableViewBtn.textContent = 'Table View';
    tableViewBtn.className = 'bg-gray-300 text-gray-800 px-4 py-2 rounded-r-md';
    tableViewBtn.id = 'table-view-btn';
    tableViewBtn.onclick = () => switchView('table');

    toggleContainer.appendChild(cardViewBtn);
    toggleContainer.appendChild(tableViewBtn);
    container.appendChild(toggleContainer);

    // Add content containers
    const cardContainer = document.createElement('div');
    cardContainer.id = 'card-view-container';

    const tableContainer = document.createElement('div');
    tableContainer.id = 'table-view-container';
    tableContainer.style.display = 'none';

    container.appendChild(cardContainer);
    container.appendChild(tableContainer);
}

/**
 * Switch between card and table views
 */
function switchView(viewMode) {
    const cardContainer = document.getElementById('card-view-container');
    const tableContainer = document.getElementById('table-view-container');
    const cardBtn = document.getElementById('card-view-btn');
    const tableBtn = document.getElementById('table-view-btn');

    if (viewMode === 'card') {
        cardContainer.style.display = 'block';
        tableContainer.style.display = 'none';
        cardBtn.className = 'bg-blue-600 text-white px-4 py-2 rounded-l-md';
        tableBtn.className = 'bg-gray-300 text-gray-800 px-4 py-2 rounded-r-md';
    } else {
        cardContainer.style.display = 'none';
        tableContainer.style.display = 'block';
        cardBtn.className = 'bg-gray-300 text-gray-800 px-4 py-2 rounded-l-md';
        tableBtn.className = 'bg-blue-600 text-white px-4 py-2 rounded-r-md';
    }
}

/**
 * Display the fetched transcripts in the UI
 */
function displayTranscripts(patients) {
    // Display as cards
    displayCardView(patients);

    // Display as table
    displayTableView(patients);
}

/**
 * Display patients data in card format
 */
function displayCardView(patients) {
    const cardContainer = document.getElementById('card-view-container');

    // Create a container for each patient's transcripts
    patients.forEach((patient, index) => {
        const transcriptCard = document.createElement('div');
        transcriptCard.className = 'bg-white shadow-lg rounded-lg p-6 mb-6';

        // Create header with patient info
        const header = document.createElement('div');
        header.className = 'mb-4 pb-2 border-b';

        const patientName = patient.name || patient.patient_name || `Patient ${index + 1}`;

        header.innerHTML = `
            <h3 class="text-xl font-semibold text-gray-800">${patientName}</h3>
            <div class="flex flex-wrap gap-2 mt-2">
                ${patient.age || patient.patient_age ?
                `<span class="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">Age: ${patient.age || patient.patient_age}</span>` : ''}
                ${patient.gender || patient.patient_gender ?
                `<span class="bg-purple-100 text-purple-800 px-2 py-1 rounded text-sm">Gender: ${patient.gender || patient.patient_gender}</span>` : ''}
            </div>
        `;

        // Create content with transcript details
        const content = document.createElement('div');

        // Add main transcript data
        if (patient.medical_information) {
            content.appendChild(createTranscriptSection('Medical Information', patient.medical_information));
        }

        if (patient.medications) {
            content.appendChild(createTranscriptSection('Medications', patient.medications));
        }

        if (patient.vital_signs) {
            content.appendChild(createTranscriptSection('Vital Signs', patient.vital_signs));
        }

        if (patient.allergies) {
            content.appendChild(createTranscriptSection('Allergies', patient.allergies));
        }

        // Create view raw JSON button
        const viewRawButton = document.createElement('button');
        viewRawButton.textContent = 'View Raw JSON';
        viewRawButton.className = 'mt-4 bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded';
        viewRawButton.onclick = () => showRawJson(patient);

        // Assemble the card
        transcriptCard.appendChild(header);
        transcriptCard.appendChild(content);
        transcriptCard.appendChild(viewRawButton);
        cardContainer.appendChild(transcriptCard);
    });
}

/**
 * Display patients data in table format
 */
function displayTableView(patients) {
    const tableContainer = document.getElementById('table-view-container');

    // Create table
    const table = document.createElement('table');
    table.className = 'min-w-full bg-white border border-gray-300 rounded-lg overflow-hidden';

    // Create table header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');

    const headers = ['Patient', 'Age/Gender', 'Medical Info', 'Medications', 'Vital Signs', 'Allergies', 'Actions'];

    headers.forEach(header => {
        const th = document.createElement('th');
        th.className = 'table-header';
        th.textContent = header;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create table body
    const tbody = document.createElement('tbody');

    patients.forEach((patient, index) => {
        const row = document.createElement('tr');
        row.className = index % 2 === 0 ? 'bg-white' : 'bg-gray-50';

        // Patient Name
        const nameCell = document.createElement('td');
        nameCell.className = 'table-cell';
        nameCell.textContent = patient.name || patient.patient_name || `Patient ${index + 1}`;

        // Age/Gender
        const ageGenderCell = document.createElement('td');
        ageGenderCell.className = 'table-cell';

        const ageGenderText = [
            patient.age || patient.patient_age ? `Age: ${patient.age || patient.patient_age}` : '',
            patient.gender || patient.patient_gender ? `Gender: ${patient.gender || patient.patient_gender}` : ''
        ].filter(Boolean).join(', ');

        ageGenderCell.textContent = ageGenderText || 'N/A';

        // Medical Info
        const medicalInfoCell = document.createElement('td');
        medicalInfoCell.className = 'table-cell';
        medicalInfoCell.innerHTML = formatCellContent(patient.medical_information);

        // Medications
        const medsCell = document.createElement('td');
        medsCell.className = 'table-cell';
        medsCell.innerHTML = formatCellContent(patient.medications);

        // Vital Signs
        const vitalsCell = document.createElement('td');
        vitalsCell.className = 'table-cell';
        vitalsCell.innerHTML = formatCellContent(patient.vital_signs);

        // Allergies
        const allergiesCell = document.createElement('td');
        allergiesCell.className = 'table-cell';
        allergiesCell.innerHTML = formatCellContent(patient.allergies);

        // Actions
        const actionsCell = document.createElement('td');
        actionsCell.className = 'table-cell';

        const viewButton = document.createElement('button');
        viewButton.textContent = 'View Details';
        viewButton.className = 'bg-blue-500 hover:bg-blue-700 text-white font-bold py-1 px-2 rounded text-sm';
        viewButton.onclick = () => showRawJson(patient);

        actionsCell.appendChild(viewButton);

        // Add cells to row
        row.appendChild(nameCell);
        row.appendChild(ageGenderCell);
        row.appendChild(medicalInfoCell);
        row.appendChild(medsCell);
        row.appendChild(vitalsCell);
        row.appendChild(allergiesCell);
        row.appendChild(actionsCell);

        tbody.appendChild(row);
    });

    table.appendChild(tbody);
    tableContainer.appendChild(table);
}

/**
 * Format cell content for table view
 */
function formatCellContent(data) {
    if (!data) return '<span class="text-gray-400">N/A</span>';

    if (typeof data === 'string') {
        return data.length > 100 ? `${data.substring(0, 100)}...` : data;
    } else if (Array.isArray(data)) {
        return data.length > 0 ?
            `<span class="font-medium">${data.length}</span> item(s)` :
            '<span class="text-gray-400">None</span>';
    } else if (typeof data === 'object') {
        return '<span class="font-medium">View details</span>';
    }

    return String(data);
}

/**
 * Create a section for a specific type of transcript data
 */
function createTranscriptSection(title, data) {
    const section = document.createElement('div');
    section.className = 'mb-4';

    const sectionTitle = document.createElement('h4');
    sectionTitle.className = 'text-lg font-medium text-gray-700 mb-2';
    sectionTitle.textContent = title;

    section.appendChild(sectionTitle);

    // Handle different data types
    if (typeof data === 'string') {
        const content = document.createElement('p');
        content.className = 'text-gray-600';
        content.textContent = data;
        section.appendChild(content);
    } else if (Array.isArray(data)) {
        const list = document.createElement('ul');
        list.className = 'list-disc pl-5';

        data.forEach(item => {
            const listItem = document.createElement('li');
            listItem.className = 'text-gray-600';
            listItem.textContent = typeof item === 'object' ? JSON.stringify(item) : item;
            list.appendChild(listItem);
        });

        section.appendChild(list);
    } else if (typeof data === 'object' && data !== null) {
        const table = document.createElement('table');
        table.className = 'min-w-full text-sm';

        for (const [key, value] of Object.entries(data)) {
            const row = document.createElement('tr');

            const keyCell = document.createElement('td');
            keyCell.className = 'py-1 pr-4 font-medium';
            keyCell.textContent = key;

            const valueCell = document.createElement('td');
            valueCell.className = 'py-1';
            valueCell.textContent = typeof value === 'object' ? JSON.stringify(value) : value;

            row.appendChild(keyCell);
            row.appendChild(valueCell);
            table.appendChild(row);
        }

        section.appendChild(table);
    }

    return section;
}

/**
 * Show the raw JSON data in a modal
 */
function showRawJson(data) {
    // Use the existing JSON modal creation functionality
    createJsonModal(data);
}

// Event listener for the transcript search button
document.addEventListener('DOMContentLoaded', function () {
    const searchButton = document.getElementById('search-transcripts-button');
    if (searchButton) {
        searchButton.addEventListener('click', function () {
            const userId = document.getElementById('transcript-user-id').value;
            if (userId) {
                fetchTranscriptsByUser(userId);
            } else {
                const errorContainer = document.getElementById('transcript-error');
                errorContainer.textContent = 'Please enter a User ID';
                errorContainer.style.display = 'block';
            }
        });
    }
});
