// Smart Resume Reviewer - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeFileHandling();
    initializeFormValidation();
    initializeTooltips();
    initializeCopyFunctionality();
});

// File handling functionality
function initializeFileHandling() {
    const fileInput = document.getElementById('resume_file');
    const textInput = document.getElementById('resume_text');
    
    if (!fileInput || !textInput) return;
    
    // Handle file selection
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        
        if (file) {
            // Clear text input when file is selected
            textInput.value = '';
            
            // Validate file
            if (!validateFile(file)) {
                e.target.value = '';
                return;
            }
            
            // Show file info
            showFileInfo(file);
        }
    });
    
    // Handle text input
    textInput.addEventListener('input', function(e) {
        if (e.target.value.trim().length > 0) {
            // Clear file input when text is entered
            fileInput.value = '';
            hideFileInfo();
        }
    });
    
    // Drag and drop functionality
    initializeDragAndDrop();
}

// File validation
function validateFile(file) {
    const maxSize = 16 * 1024 * 1024; // 16MB
    const allowedTypes = ['.pdf', '.txt'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (file.size > maxSize) {
        showAlert('File size exceeds 16MB limit. Please choose a smaller file.', 'error');
        return false;
    }
    
    if (!allowedTypes.includes(fileExtension)) {
        showAlert('Please upload a PDF or TXT file only.', 'error');
        return false;
    }
    
    return true;
}

// Show file information
function showFileInfo(file) {
    const fileInfo = document.getElementById('fileInfo') || createFileInfoElement();
    const fileSize = (file.size / 1024 / 1024).toFixed(2);
    
    fileInfo.innerHTML = `
        <div class="alert alert-success d-flex align-items-center" role="alert">
            <i data-feather="file" class="me-2"></i>
            <div>
                <strong>${file.name}</strong><br>
                <small>Size: ${fileSize} MB</small>
            </div>
        </div>
    `;
    
    // Re-initialize feather icons
    feather.replace();
}

// Hide file information
function hideFileInfo() {
    const fileInfo = document.getElementById('fileInfo');
    if (fileInfo) {
        fileInfo.innerHTML = '';
    }
}

// Create file info element
function createFileInfoElement() {
    const fileInput = document.getElementById('resume_file');
    let fileInfo = document.getElementById('fileInfo');
    
    if (!fileInfo) {
        fileInfo = document.createElement('div');
        fileInfo.id = 'fileInfo';
        fileInput.parentNode.appendChild(fileInfo);
    }
    
    return fileInfo;
}

// Form validation
function initializeFormValidation() {
    const form = document.getElementById('resumeForm');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            return false;
        }
        
        showLoadingState();
    });
}

// Validate form before submission
function validateForm() {
    const jobRole = document.getElementById('job_role').value.trim();
    const fileInput = document.getElementById('resume_file');
    const textInput = document.getElementById('resume_text');
    
    // Check job role
    if (!jobRole) {
        showAlert('Please enter a target job role.', 'error');
        return false;
    }
    
    // Check resume content
    const hasFile = fileInput && fileInput.files.length > 0;
    const hasText = textInput && textInput.value.trim().length > 0;
    
    if (!hasFile && !hasText) {
        showAlert('Please either upload a resume file or paste your resume text.', 'error');
        return false;
    }
    
    return true;
}

// Show loading state
function showLoadingState() {
    const btn = document.getElementById('analyzeBtn');
    const btnText = document.getElementById('btnText');
    const spinner = document.getElementById('btnSpinner');
    
    if (btn) {
        btn.disabled = true;
        btn.classList.add('disabled');
    }
    
    if (btnText) {
        btnText.textContent = 'Analyzing Resume...';
    }
    
    if (spinner) {
        spinner.classList.remove('d-none');
    }
}

// Drag and drop functionality
function initializeDragAndDrop() {
    const dropZone = document.querySelector('.border.rounded.p-4');
    if (!dropZone) return;
    
    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropZone.classList.add('border-primary', 'bg-primary-subtle');
    });
    
    dropZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        dropZone.classList.remove('border-primary', 'bg-primary-subtle');
    });
    
    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        dropZone.classList.remove('border-primary', 'bg-primary-subtle');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const fileInput = document.getElementById('resume_file');
            if (fileInput) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
    });
}

// Initialize tooltips
function initializeTooltips() {
    // Initialize Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// Copy functionality
function initializeCopyFunctionality() {
    // This will be used by the copy button in results page
    window.copyToClipboard = function(text, button) {
        navigator.clipboard.writeText(text).then(function() {
            showCopySuccess(button);
        }).catch(function(err) {
            console.error('Failed to copy text: ', err);
            showAlert('Failed to copy text to clipboard.', 'error');
        });
    };
}

// Show copy success feedback
function showCopySuccess(button) {
    if (!button) return;
    
    const originalHTML = button.innerHTML;
    button.innerHTML = '<i data-feather="check" class="me-1"></i>Copied!';
    button.classList.remove('btn-outline-secondary');
    button.classList.add('btn-success');
    
    setTimeout(() => {
        button.innerHTML = originalHTML;
        button.classList.remove('btn-success');
        button.classList.add('btn-outline-secondary');
        feather.replace();
    }, 2000);
    
    feather.replace();
}

// Alert system
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container .mt-3') || document.querySelector('.container');
    if (!alertContainer) return;
    
    const alertClass = type === 'error' ? 'danger' : type;
    const iconName = type === 'error' ? 'alert-circle' : 'info';
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${alertClass} alert-dismissible fade show`;
    alert.setAttribute('role', 'alert');
    
    alert.innerHTML = `
        <i data-feather="${iconName}" class="me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert at the beginning of container
    alertContainer.insertBefore(alert, alertContainer.firstChild);
    
    // Re-initialize feather icons
    feather.replace();
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.classList.remove('show');
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.parentNode.removeChild(alert);
                }
            }, 150);
        }
    }, 5000);
}

// Smooth scrolling for anchor links
document.addEventListener('click', function(e) {
    if (e.target.matches('a[href^="#"]')) {
        e.preventDefault();
        const targetId = e.target.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        
        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const form = document.getElementById('resumeForm');
        if (form && validateForm()) {
            form.submit();
        }
    }
});

// Auto-save form data to localStorage
function initializeAutoSave() {
    const form = document.getElementById('resumeForm');
    if (!form) return;
    
    const inputs = form.querySelectorAll('input[type="text"], textarea');
    
    // Load saved data
    inputs.forEach(input => {
        const savedValue = localStorage.getItem('resume_form_' + input.id);
        if (savedValue && !input.value) {
            input.value = savedValue;
        }
    });
    
    // Save data on input
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            localStorage.setItem('resume_form_' + input.id, input.value);
        });
    });
    
    // Clear saved data on successful submission
    form.addEventListener('submit', function() {
        inputs.forEach(input => {
            localStorage.removeItem('resume_form_' + input.id);
        });
    });
}

// Initialize auto-save when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeAutoSave);

// Utility function to format file sizes
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Utility function to get file extension
function getFileExtension(filename) {
    return filename.slice((filename.lastIndexOf(".") - 1 >>> 0) + 2);
}

// Performance monitoring
function logPageLoadTime() {
    window.addEventListener('load', function() {
        const loadTime = performance.now();
        console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);
    });
}

// Initialize performance monitoring
logPageLoadTime();
