/**
 * BTG - Main JavaScript
 * 
 * This file contains the client-side JavaScript for the BTG application.
 * It handles API calls, UI interactions, and dynamic content updates.
 */

/**
 * Update a sprint container with fresh content
 * @param {string} sprintId - The ID of the sprint to update
 * @returns {Promise} - A promise that resolves when the update is complete
 */
function updateSprintContainer(sprintId) {
    return new Promise((resolve, reject) => {
        fetch(`/api/sprints/${sprintId}/content`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                // Find the sprint container
                const sprintContainer = document.querySelector(`.sprint-card[data-sprint-id="${sprintId}"]`);
                if (sprintContainer) {
                    // Update the tasks and issues sections
                    const tasksContainer = sprintContainer.querySelector('.tasks-container');
                    const issuesContainer = sprintContainer.querySelector('.issues-container');
                    
                    if (tasksContainer) {
                        tasksContainer.innerHTML = data.data.tasksHtml || '';
                    }
                    
                    if (issuesContainer) {
                        issuesContainer.innerHTML = data.data.issuesHtml || '';
                    }
                    
                    resolve();
                }
            } else {
                reject(new Error('Failed to update sprint content'));
            }
        })
        .catch(error => {
            console.error('Error updating sprint container:', error);
            reject(error);
        });
    });
}

/**
 * Show a notification message
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, error, warning, info)
 */
function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification-toast`;
    notification.innerHTML = message;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Show with animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Hide after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

/**
 * Universal utility function to close any form container
 * @param {string} containerId - The ID of the form container to close
 */
function closeFormContainer(containerId) {
    // Clear the form container
    const formContainer = document.getElementById(containerId);
    if (formContainer) {
        formContainer.innerHTML = '';
    }
}

/**
 * Close the task form for a specific sprint
 * @param {string} sprintId - The ID of the sprint
 */
function closeTaskForm(sprintId) {
    closeFormContainer(`task-form-container-${sprintId}`);
}

/**
 * Close the issue form for a specific sprint
 * @param {string} sprintId - The ID of the sprint
 */
function closeIssueForm(sprintId) {
    closeFormContainer(`issue-form-container-${sprintId}`);
}

/**
 * Close any modal by ID
 * @param {string} modalId - The ID of the modal to close
 */
function closeModal(modalId) {
    // Dispatch the close-modal event that Alpine.js listens for
    document.dispatchEvent(new CustomEvent('close-modal', {
        detail: {
            id: modalId
        }
    }));
}

/**
 * Close the sprint form for a specific project
 * @param {string} projectId - The ID of the project
 */
function closeSprintForm(projectId) {
    const formContainer = document.getElementById(`sprint-form-container-${projectId}`);
    if (formContainer) {
        formContainer.innerHTML = '';
    }
}

/**
 * Close the sprint edit form for a specific sprint
 * @param {string} sprintId - The ID of the sprint
 */
function closeSprintEditForm(sprintId) {
    const formContainer = document.getElementById(`sprint-${sprintId}`);
    if (formContainer) {
        // Get the original sprint HTML
        htmx.ajax('GET', `/htmx/sprints/${sprintId}`, {target: formContainer});
    }
}

/**
 * Close the project form
 */
function closeProjectForm() {
    closeFormContainer('project-form-container');
}

/**
 * Initialize task-related event listeners
 */
function initializeTaskEventListeners() {
    // Event delegation for task completion toggle
    document.addEventListener('click', function(event) {
        // Check if the click was on a task completion checkbox
        if (event.target.matches('.task-completion-checkbox')) {
            const taskId = event.target.dataset.taskId;
            const isCompleted = event.target.checked;
            
            // Update task completion status
            fetch(`/api/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    completed: isCompleted
                })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    // Update UI to reflect the new completion status
                    const taskItem = document.querySelector(`.task-item[data-task-id="${taskId}"]`);
                    if (taskItem) {
                        if (isCompleted) {
                            taskItem.classList.add('completed');
                        } else {
                            taskItem.classList.remove('completed');
                        }
                    }
                    
                    // Show notification
                    showNotification(`Task marked as ${isCompleted ? 'completed' : 'incomplete'}`);
                }
            })
            .catch(error => {
                console.error('Error updating task completion:', error);
                showNotification('Error updating task. Please try again.', 'error');
                
                // Revert checkbox state on error
                event.target.checked = !isCompleted;
            });
        }
    });
    
    // Add task button click
    document.querySelectorAll('.add-task-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const sprintId = this.dataset.sprintId;
            openTaskModal(sprintId);
        });
    });
    
    // Save task button click - only add if element exists
    const saveTaskBtn = document.getElementById('saveTaskBtn');
    if (saveTaskBtn) {
        saveTaskBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            e.preventDefault();
            saveTask();
        });
    }
}

/**
 * Initialize issue-related event listeners
 */
function initializeIssueEventListeners() {
    // Add issue button click
    document.querySelectorAll('.add-issue-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const sprintId = this.dataset.sprintId;
            openIssueModal(sprintId);
        });
    });
    
    // Save issue button click - only add if element exists
    const saveIssueBtn = document.getElementById('saveIssueBtn');
    if (saveIssueBtn) {
        saveIssueBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            e.preventDefault();
            saveIssue();
        });
    }
}

/**
 * Initialize keyboard shortcuts for the application
 */
function initializeKeyboardShortcuts() {
    // Add global keydown event listener for form submission shortcuts (Cmd/Ctrl + Enter)
    document.addEventListener('keydown', function(e) {
        // Check if Cmd (Mac) or Ctrl (Windows/Linux) key is pressed along with Enter
        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
            e.preventDefault(); // Prevent default behavior
            
            // Get the currently active/focused element
            const activeElement = document.activeElement;
            
            // Find the closest form to the active element
            const form = activeElement.closest('form');
            
            if (form) {
                // If we found a form, submit it
                console.log('Submitting form via keyboard shortcut:', form.id || 'unnamed form');
                
                // For forms with a submit button, click the submit button instead of using form.submit()
                // This ensures any click handlers on the submit button are executed
                const submitButton = form.querySelector('button[type="submit"]');
                if (submitButton) {
                    submitButton.click();
                } else {
                    // Fallback to form.submit() if no submit button is found
                    form.submit();
                }
                return;
            }
            
            // Legacy modal support (fallback for older code)
            // Check which modal is currently active and trigger the appropriate save button
            if (document.getElementById('projectModal')?.classList.contains('show')) {
                // Project modal is active, trigger save project
                document.getElementById('saveProjectBtn')?.click();
            } else if (document.getElementById('sprintModal')?.classList.contains('show')) {
                // Sprint modal is active, trigger save sprint
                document.getElementById('saveSprintBtn')?.click();
            } else if (document.getElementById('taskModal')?.classList.contains('show')) {
                // Task modal is active, trigger save task
                document.getElementById('saveTaskBtn')?.click();
            } else if (document.getElementById('issueModal')?.classList.contains('show')) {
                // Issue modal is active, trigger save issue
                document.getElementById('saveIssueBtn')?.click();
            } else {
                // Check for specific HTMX forms that might not be focused but are visible
                const htmxForms = [
                    'htmx-task-form',
                    'htmx-issue-form',
                    'htmx-sprint-form',
                    'htmx-project-form'
                ];
                
                for (const formId of htmxForms) {
                    const htmxForm = document.getElementById(formId);
                    if (htmxForm) {
                        console.log('Submitting HTMX form via keyboard shortcut:', formId);
                        const submitBtn = htmxForm.querySelector('button[type="submit"]');
                        if (submitBtn) {
                            submitBtn.click();
                            return;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Auto-expand textareas with the 'auto-expand' class
 * This function will be called on page load and after HTMX swaps
 */
function initAutoExpandTextareas() {
    // Get all textareas with the auto-expand class
    const textareas = document.querySelectorAll('textarea.auto-expand');
    
    // Auto-expand each textarea
    textareas.forEach(function(textarea) {
        // Set initial height based on content
        textarea.style.height = '';
        textarea.style.height = textarea.scrollHeight + 'px';
        
        // Add event listeners if they don't already exist
        if (!textarea.dataset.autoExpandInitialized) {
            // Input event for when user types
            textarea.addEventListener('input', function() {
                this.style.height = '';
                this.style.height = this.scrollHeight + 'px';
            });
            
            // Click event for when user clicks
            textarea.addEventListener('click', function() {
                this.style.height = '';
                this.style.height = this.scrollHeight + 'px';
            });
            
            // Focus event for when user tabs into the textarea
            textarea.addEventListener('focus', function() {
                this.style.height = '';
                this.style.height = this.scrollHeight + 'px';
            });
            
            // Mark as initialized
            textarea.dataset.autoExpandInitialized = 'true';
        }
    });
}

/**
 * Initialize Alpine.js components after HTMX content swaps
 * This is necessary because Alpine.js doesn't automatically initialize
 * components added to the DOM after the initial page load
 */
function initAlpineAfterHtmxSwap() {
    // Check if Alpine.js is available
    if (window.Alpine) {
        // Get all elements with x-data attribute that haven't been initialized by Alpine
        document.querySelectorAll('[x-data]:not([x-data-initialized])').forEach(el => {
            // Mark as initialized to avoid duplicate initialization
            el.setAttribute('x-data-initialized', 'true');
            
            // Initialize Alpine.js on this element
            window.Alpine.initTree(el);
        });
    }
}

/**
 * Open a delete confirmation modal
 * @param {string} modalId - The ID of the modal to open
 * @param {string} title - The title for the modal
 * @param {string} message - The confirmation message to display
 * @param {Function} onConfirm - The function to call when delete is confirmed
 */
function openDeleteConfirmationModal(modalId, title, message, onConfirm) {
    console.log('Opening modal:', modalId, title);
    
    // Set the confirmation message first
    const contentElement = document.getElementById(`${modalId}-content`);
    if (contentElement) {
        console.log('Found content element:', contentElement);
        
        // Create the modal content
        contentElement.innerHTML = `
            <p class="mb-4">${message}</p>
            <div class="modal-action">
                <button class="btn btn-ghost" @click="open = false">Cancel</button>
                <button class="btn btn-error" id="${modalId}-confirm-btn">Delete</button>
            </div>
        `;
        
        // Add event listener to the confirm button
        const confirmBtn = document.getElementById(`${modalId}-confirm-btn`);
        if (confirmBtn) {
            console.log('Found confirm button:', confirmBtn);
            
            // Remove any existing event listeners
            const newConfirmBtn = confirmBtn.cloneNode(true);
            confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
            
            // Add the new event listener
            newConfirmBtn.addEventListener('click', function() {
                console.log('Confirm button clicked');
                
                // Close the modal
                document.dispatchEvent(new CustomEvent('close-modal', {
                    detail: {
                        id: modalId
                    }
                }));
                
                // Call the onConfirm function
                if (typeof onConfirm === 'function') {
                    onConfirm();
                }
            });
        } else {
            console.error('Confirm button not found!');
        }
    } else {
        console.error('Content element not found!', `#${modalId}-content`);
    }
    
    // Now dispatch the open-modal event that Alpine.js listens for
    console.log('Dispatching open-modal event');
    document.dispatchEvent(new CustomEvent('open-modal', {
        detail: {
            id: modalId,
            title: title
        }
    }));
}

/**
 * Handle delete action with confirmation modal instead of browser alert
 * @param {Element} element - The element that triggered the delete action
 * @param {string} url - The URL to send the delete request to
 * @param {string} message - The confirmation message to display
 * @param {string} itemType - The type of item being deleted (project, sprint, task, issue)
 */
function handleDelete(element, url, message, itemType) {
    openDeleteConfirmationModal(
        'delete-confirmation-modal',
        `Confirm Delete ${itemType}`,
        message,
        function() {
            // Send the DELETE request using HTMX
            htmx.ajax('DELETE', url, {
                target: '#appMainContainer',
                swap: 'innerHTML'
            });
        }
    );
}

/**
 * Initialize delete button event listeners
 * This replaces the hx-confirm functionality with modal dialogs
 */
function initializeDeleteEventListeners() {
    // Project delete buttons
    document.querySelectorAll('[data-delete-project]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const projectId = this.dataset.projectId;
            const url = this.dataset.deleteUrl;
            const message = "Are you sure you want to delete this project? This will also delete all sprints, tasks, and issues associated with this project.";
            
            console.log('Project delete clicked:', projectId, url);
            handleDelete(this, url, message, 'Project');
        });
    });
    
    // Sprint delete buttons
    document.querySelectorAll('[data-delete-sprint]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const sprintId = this.dataset.sprintId;
            const url = this.dataset.deleteUrl;
            const message = "Are you sure you want to delete this sprint? This will also delete all tasks and issues in this sprint.";
            
            console.log('Sprint delete clicked:', sprintId, url);
            handleDelete(this, url, message, 'Sprint');
        });
    });
    
    // Task delete buttons
    document.querySelectorAll('[data-delete-task]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const taskId = this.dataset.taskId;
            const url = this.dataset.deleteUrl;
            const message = "Are you sure you want to delete this task?";
            
            console.log('Task delete clicked:', taskId, url);
            handleDelete(this, url, message, 'Task');
        });
    });
    
    // Issue delete buttons
    document.querySelectorAll('[data-delete-issue]').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const issueId = this.dataset.issueId;
            const url = this.dataset.deleteUrl;
            const message = "Are you sure you want to delete this issue?";
            
            console.log('Issue delete clicked:', issueId, url);
            handleDelete(this, url, message, 'Issue');
        });
    });
}

// Initialize everything when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize task event listeners
    initializeTaskEventListeners();
    
    // Initialize issue event listeners
    initializeIssueEventListeners();
    
    // Initialize delete event listeners
    initializeDeleteEventListeners();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
    
    // Initialize auto-expand textareas
    initAutoExpandTextareas();
    
    // Initialize Alpine.js components
    initAlpineAfterHtmxSwap();
    
    // Log initialization for debugging
    console.log('Delete event listeners initialized');
});

// Initialize Alpine.js components and auto-expand textareas after HTMX content swaps
document.body.addEventListener('htmx:afterSwap', function() {
    // Allow a small delay for the DOM to stabilize
    setTimeout(function() {
        initAlpineAfterHtmxSwap();
        initAutoExpandTextareas();
        initializeDeleteEventListeners(); // Re-initialize delete listeners after content swap
        console.log('Delete event listeners re-initialized after HTMX swap');
    }, 10);
});
