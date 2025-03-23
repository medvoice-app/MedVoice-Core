// Nurse CRUD operations
function editNurse(id, name, email) {
    document.getElementById('editNurseId').value = id;
    document.getElementById('editNurseName').value = name;
    document.getElementById('editNurseEmail').value = email;
    openEditNurseModal();
}

async function updateNurse() {
    const id = document.getElementById('editNurseId').value;
    const name = document.getElementById('editNurseName').value;
    const email = document.getElementById('editNurseEmail').value;

    const nurse = { name, email };

    try {
        await fetch(`${apiUrl}nurses/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(nurse)
        });
        fetchNurses();
        closeEditNurseModal();
    } catch (error) {
        console.error('Error updating nurse:', error);
    }
}

async function deleteNurse(id) {
    if (!confirm('Are you sure you want to delete this nurse?')) return;

    try {
        await fetch(`${apiUrl}nurses/${id}`, { method: 'DELETE' });
        fetchNurses();
    } catch (error) {
        console.error('Error deleting nurse:', error);
    }
}
