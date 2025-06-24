// Main JavaScript file for Stock & Options Tracker

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all functionality
    initializeFormValidation();
    initializeTooltips();
    initializeConfirmDialogs();
    initializeTableSorting();
    initializeNumberFormatting();
});

// Form validation and dynamic field handling
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Confirmation dialogs for delete actions
function initializeConfirmDialogs() {
    const deleteButtons = document.querySelectorAll('form[action*="delete"]');
    deleteButtons.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!confirm('Are you sure you want to delete this trade? This action cannot be undone.')) {
                event.preventDefault();
            }
        });
    });
}

// Simple table sorting functionality
function initializeTableSorting() {
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            if (header.textContent.trim() && index < 6) { // Only sort first few columns
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => sortTable(table, index));
            }
        });
    });
}

// Sort table by column index
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isNumeric = isColumnNumeric(rows, columnIndex);
    let ascending = true;
    
    // Check if already sorted and toggle direction
    const header = table.querySelectorAll('th')[columnIndex];
    if (header.classList.contains('sorted-asc')) {
        ascending = false;
        header.classList.remove('sorted-asc');
        header.classList.add('sorted-desc');
    } else {
        // Remove previous sorting indicators
        table.querySelectorAll('th').forEach(h => {
            h.classList.remove('sorted-asc', 'sorted-desc');
        });
        header.classList.add('sorted-asc');
    }
    
    rows.sort((a, b) => {
        const aValue = getCellValue(a, columnIndex);
        const bValue = getCellValue(b, columnIndex);
        
        if (isNumeric) {
            const aNum = parseFloat(aValue.replace(/[$,]/g, '')) || 0;
            const bNum = parseFloat(bValue.replace(/[$,]/g, '')) || 0;
            return ascending ? aNum - bNum : bNum - aNum;
        } else {
            return ascending ? 
                aValue.localeCompare(bValue) : 
                bValue.localeCompare(aValue);
        }
    });
    
    // Rebuild table body
    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
}

// Get cell value for sorting
function getCellValue(row, columnIndex) {
    const cell = row.cells[columnIndex];
    return cell ? cell.textContent.trim() : '';
}

// Check if column contains numeric data
function isColumnNumeric(rows, columnIndex) {
    for (let i = 0; i < Math.min(5, rows.length); i++) {
        const value = getCellValue(rows[i], columnIndex);
        const numericValue = parseFloat(value.replace(/[$,]/g, ''));
        if (!isNaN(numericValue)) {
            return true;
        }
    }
    return false;
}

// Format numbers with proper currency formatting
function initializeNumberFormatting() {
    const numberInputs = document.querySelectorAll('input[type="number"], input[step]');
    numberInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value && this.name !== 'quantity') {
                const value = parseFloat(this.value);
                if (!isNaN(value)) {
                    this.value = value.toFixed(2);
                }
            }
        });
    });
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Utility function to format percentage
function formatPercentage(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value / 100);
}

// Add visual feedback for form submissions
function addFormSubmissionFeedback() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';
            }
        });
    });
}

// Initialize advanced features
function initializeAdvancedFeatures() {
    // Auto-uppercase symbol inputs
    const symbolInputs = document.querySelectorAll('input[name="symbol"]');
    symbolInputs.forEach(input => {
        input.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    });
    
    // Real-time calculation display for options
    const premiumInput = document.querySelector('input[name="premium"]');
    const quantityInput = document.querySelector('input[name="quantity"]');
    
    if (premiumInput && quantityInput) {
        [premiumInput, quantityInput].forEach(input => {
            input.addEventListener('input', updateOptionsCalculation);
        });
    }
}

// Update options calculation display
function updateOptionsCalculation() {
    const premium = parseFloat(document.querySelector('input[name="premium"]')?.value) || 0;
    const quantity = parseInt(document.querySelector('input[name="quantity"]')?.value) || 0;
    
    if (premium > 0 && quantity > 0) {
        const totalCost = premium * quantity * 100; // Options are per 100 shares
        
        // Create or update calculation display
        let calcDisplay = document.getElementById('optionsCalculation');
        if (!calcDisplay) {
            calcDisplay = document.createElement('div');
            calcDisplay.id = 'optionsCalculation';
            calcDisplay.className = 'alert alert-info mt-2';
            
            const premiumField = document.querySelector('input[name="premium"]').closest('.col-md-4');
            if (premiumField) {
                premiumField.appendChild(calcDisplay);
            }
        }
        
        calcDisplay.innerHTML = `
            <small>
                <strong>Total Cost:</strong> ${formatCurrency(totalCost)}<br>
                <small class="text-muted">${quantity} contracts × $${premium.toFixed(2)} × 100 shares</small>
            </small>
        `;
    }
}

// Initialize all advanced features
document.addEventListener('DOMContentLoaded', function() {
    initializeAdvancedFeatures();
    addFormSubmissionFeedback();
});
