async function fetchNurses() {
    try {
        const response = await fetch(`${apiUrl}nurses/`);
        const nurses = await response.json();
        populateNurseTable(nurses);
    } catch (error) {
        console.error('Error fetching nurses:', error);
    }
}
