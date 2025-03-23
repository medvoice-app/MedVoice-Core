function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.classList.remove('hidden');

    // Focus the first input field when the modal opens - with delay to ensure DOM is ready
    setTimeout(() => {
        const firstInput = modal.querySelector('input:not([type="hidden"]):not([disabled]), textarea:not([disabled]), select:not([disabled])');
        if (firstInput) {
            firstInput.focus();
            firstInput.setAttribute('tabindex', '0');

            // For iOS/mobile devices, try to ensure the input is actually focused
            if (firstInput.nodeName === 'INPUT') {
                firstInput.click();
            }
        }

        // Call form utility function if it exists
        if (window.refreshFormElements) {
            window.refreshFormElements();
        }
    }, 150);

    // Stop scrolling on the body
    document.body.style.overflow = 'hidden';

    // Add event listener to close on escape key
    document.addEventListener('keydown', function escHandler(e) {
        if (e.key === 'Escape') {
            closeModal(modalId);
            document.removeEventListener('keydown', escHandler);
        }
    });
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;

    modal.classList.add('hidden');

    // Restore scrolling on the body
    document.body.style.overflow = 'auto';

    // Clear form fields when closing the modal
    const form = modal.querySelector('form');
    if (form) form.reset();

    // Return focus to the element that opened the modal, if possible
    if (window.lastFocusedElement) {
        setTimeout(() => {
            window.lastFocusedElement.focus();
        }, 10);
    }
}

function openEditNurseModal() {
    const modal = document.getElementById('editNurseModal');
    modal.classList.remove('hidden');

    // Focus with delay to ensure DOM is ready
    setTimeout(() => {
        const nameInput = document.getElementById('editNurseName');
        if (nameInput) {
            nameInput.focus();
            nameInput.setAttribute('tabindex', '0');
        }
    }, 150);

    // Stop scrolling on the body
    document.body.style.overflow = 'hidden';

    // Add event listener to close on escape key
    document.addEventListener('keydown', function escHandler(e) {
        if (e.key === 'Escape') {
            closeEditNurseModal();
            document.removeEventListener('keydown', escHandler);
        }
    });
}

function closeEditNurseModal() {
    const modal = document.getElementById('editNurseModal');
    if (modal) {
        modal.classList.add('hidden');

        // Restore scrolling on the body
        document.body.style.overflow = 'auto';
    }
}

// Track the last focused element to restore focus when modal closes
document.addEventListener('click', function (e) {
    if (e.target.getAttribute('onclick')?.includes('openModal') ||
        e.target.getAttribute('onclick')?.includes('openEditNurseModal')) {
        window.lastFocusedElement = e.target;
    }
});

// Add enhanced stop propagation that also prevents default when needed
function stopPropagation(event) {
    if (!event) return;

    event.stopPropagation();

    // Only prevent default for certain elements like buttons in forms
    if (event.target.tagName === 'BUTTON' &&
        event.target.type !== 'submit' &&
        event.target.closest('form')) {
        event.preventDefault();
    }
}

// Ensure form inputs don't trigger modal closing
document.addEventListener('DOMContentLoaded', function () {
    const modalContents = document.querySelectorAll('.modal-content');
    modalContents.forEach(content => {
        content.addEventListener('click', stopPropagation);

        // Prevent default on form submission inside modals
        const forms = content.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function (e) {
                e.preventDefault();
            });
        });
    });
});
