document.getElementById('searchBtn').addEventListener('click', async function() {
    try {
        // Change the button color to red   
        this.classList.remove("bg-blue-500", "hover:bg-blue-700");
        this.classList.add("bg-red-500", "hover:bg-red-700");
        
        const userId = document.getElementById('user_id').value;
        const response = await fetch(`${apiUrl}get_audio/${userId}`);
        const data = await response.json();
        
        document.getElementById('audioURL').value = data.urls.join('\n');
    } catch (error) {
        console.error('Error fetching audio URLs:', error);
        document.getElementById('audioURL').value = 'Error: Failed to fetch audio URLs';
    }
});
