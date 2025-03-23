document.getElementById('signupButton').addEventListener('click', async function () {
    const name = document.getElementById('signupName').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value;

    // Add email validation
    if (!name) {
        alert('Please enter your name');
        document.getElementById('signupName').focus();
        return;
    }

    if (!validateEmail(email)) {
        alert('Please enter a valid email address');
        document.getElementById('signupEmail').focus();
        return;
    }

    if (!password) {
        alert('Please enter a password');
        document.getElementById('signupPassword').focus();
        return;
    }

    // Add button loading state
    this.disabled = true;
    this.textContent = 'Signing up...';

    try {
        const response = await fetch(`${apiUrl}nurses/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Signup failed');
        }

        if (data.detail) {
            alert(data.detail);
        } else {
            alert('Signup successful');
            closeModal('signupModal');
            // Refresh the nurses table
            await fetchNurses();
        }
    } catch (error) {
        console.error('Error during signup:', error);
        alert(error.message || 'An error occurred during signup. Please try again.');
    } finally {
        // Reset button state
        this.disabled = false;
        this.textContent = 'Sign Up';
    }
});

// Add this email validation function
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

document.getElementById('loginButton').addEventListener('click', async function () {
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!validateEmail(email)) {
        alert('Please enter a valid email address');
        document.getElementById('loginEmail').focus();
        return;
    }

    if (!password) {
        alert('Please enter your password');
        document.getElementById('loginPassword').focus();
        return;
    }

    // Add button loading state
    this.disabled = true;
    this.textContent = 'Logging in...';

    try {
        const response = await fetch(`${apiUrl}nurses/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }

        if (data.detail) {
            alert(data.detail);
        } else {
            alert('Login successful\nNurse ID: ' + data.nurse_id);
            closeModal('loginModal');
            // Refresh the nurses table
            await fetchNurses();
        }
    } catch (error) {
        console.error('Error during login:', error);
        alert(error.message || 'An error occurred during login. Please try again.');
    } finally {
        // Reset button state
        this.disabled = false;
        this.textContent = 'Login';
    }
});

// Add click event listeners to prevent modal closing when clicking on the form
document.addEventListener('DOMContentLoaded', function () {
    // Prevent form clicks from closing the modal
    const modalForms = document.querySelectorAll('.modal-content');
    modalForms.forEach(form => {
        form.addEventListener('click', function (e) {
            e.stopPropagation();
        });
    });
});
