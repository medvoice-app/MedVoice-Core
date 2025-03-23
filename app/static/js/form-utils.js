/**
 * Form utilities to improve interactivity and fix common input issues
 */

// Run when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // Fix all form elements on page load
    fixAllFormElements();

    // Set up a mutation observer to handle dynamically added elements
    observeDynamicElements();

    // Add event listeners to handle focus/blur events
    setupFocusManagement();
});

/**
 * Fix all interactive form elements on the page
 */
function fixAllFormElements() {
    // Handle all input types, textareas, and selects
    const formElements = document.querySelectorAll('input, textarea, select');

    formElements.forEach(element => {
        // Replace the element with a clone to remove any problematic event listeners
        if (!element.hasAttribute('data-fixed')) {
            const newElement = element.cloneNode(true);

            // Preserve any existing event listeners that we want to keep
            if (element.id) {
                preserveEventListeners(element.id, newElement);
            }

            // Remove readonly attribute except for specific elements
            if (newElement.hasAttribute('readonly') &&
                !newElement.id?.includes('conversation') &&
                !newElement.classList.contains('no-edit')) {
                newElement.removeAttribute('readonly');
            }

            // Make sure tabindex is set for focusable elements
            newElement.setAttribute('tabindex', '0');

            // Mark as fixed to avoid re-processing
            newElement.setAttribute('data-fixed', 'true');

            // Enable pointer events explicitly
            newElement.style.pointerEvents = 'auto';

            // Replace the original element with the fixed one
            if (element.parentNode) {
                element.parentNode.replaceChild(newElement, element);
            }

            // For textareas, ensure they properly resize
            if (newElement.tagName === 'TEXTAREA') {
                makeTextareaResponsive(newElement);
            }
        }
    });
}

/**
 * Make textareas resize properly based on content
 */
function makeTextareaResponsive(textarea) {
    // Skip if it's already responsive or meant to be fixed size
    if (textarea.classList.contains('fixed-size')) return;

    // Function to adjust height based on content
    const adjustHeight = () => {
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight) + 'px';
    };

    // Set initial height
    if (!textarea.getAttribute('readonly')) {
        // Add event listeners for content changes
        textarea.addEventListener('input', adjustHeight);
        textarea.addEventListener('focus', adjustHeight);
    }

    // Initial adjustment
    setTimeout(adjustHeight, 10);
}

/**
 * Preserve important event listeners when replacing elements
 */
function preserveEventListeners(elementId, newElement) {
    // Handle special cases based on element ID
    switch (elementId) {
        case 'signupButton':
        case 'loginButton':
            newElement.addEventListener('click', function () {
                const originalButton = document.getElementById(elementId);
                if (originalButton && originalButton.click) {
                    originalButton.click();
                }
            });
            break;
        case 'conversation':
            // Make sure the conversation textarea remains readonly
            newElement.setAttribute('readonly', 'readonly');
            break;
    }
}

/**
 * Set up a mutation observer to detect and fix dynamically added form elements
 */
function observeDynamicElements() {
    const observer = new MutationObserver((mutations) => {
        let shouldFix = false;

        mutations.forEach(mutation => {
            if (mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const formElements = node.querySelectorAll('input, textarea, select');
                        if (formElements.length > 0) shouldFix = true;
                    }
                });
            }
        });

        if (shouldFix) {
            setTimeout(fixAllFormElements, 50);
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

/**
 * Set up focus management for improved accessibility and usability
 */
function setupFocusManagement() {
    // Fix focus trap in modals
    document.querySelectorAll('.modal-content').forEach(modal => {
        const focusableElements = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');

        if (focusableElements.length > 0) {
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            // Loop focus within the modal
            lastElement.addEventListener('keydown', function (e) {
                if (e.key === 'Tab' && !e.shiftKey) {
                    e.preventDefault();
                    firstElement.focus();
                }
            });

            firstElement.addEventListener('keydown', function (e) {
                if (e.key === 'Tab' && e.shiftKey) {
                    e.preventDefault();
                    lastElement.focus();
                }
            });
        }
    });

    // Ensure input fields are properly focused on click
    document.querySelectorAll('input, textarea, select').forEach(element => {
        element.addEventListener('click', function (e) {
            this.focus();
            e.stopPropagation();
        });
    });
}

/**
 * Function that can be called from anywhere to refresh all form elements
 */
function refreshFormElements() {
    setTimeout(fixAllFormElements, 10);
}

// Export function for external use
window.refreshFormElements = refreshFormElements;
