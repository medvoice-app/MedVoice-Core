// Add a helper function to handle API responses consistently
async function handleApiResponse(response) {
    const data = await response.json();

    if (!response.ok) {
        // Extract error message from response
        const errorMessage = data.detail || 'An error occurred';
        throw new Error(errorMessage);
    }

    return data;
}

// Add a function to fetch nurses with error handling
async function fetchNurses() {
    console.log('Fetching nurses...');
    const loadingElement = document.getElementById('nurse-loading');
    const errorElement = document.getElementById('nurse-error');

    // Show loading indicator
    if (loadingElement) loadingElement.style.display = 'block';
    if (errorElement) errorElement.style.display = 'none';

    try {
        const response = await fetch(`${apiUrl}nurses/`);
        const data = await handleApiResponse(response);
        console.log('Nurses fetched:', data);
        populateNurseTable(data);

        // Hide loading indicator
        if (loadingElement) loadingElement.style.display = 'none';
    } catch (error) {
        console.error('Error fetching nurses:', error);

        // Show error message
        if (errorElement) {
            errorElement.textContent = `Failed to load nurses: ${error.message}`;
            errorElement.style.display = 'block';
        }

        if (loadingElement) loadingElement.style.display = 'none';
    }
}

// Export functions for use in other modules
