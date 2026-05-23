// Aviation Monitoring System - Main JavaScript

$(document).ready(function() {
    console.log('Aviation Monitoring System Loaded');
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').not('.alert-permanent').fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
    
    // Confirm delete actions
    $('.btn-danger[href*="delete"]').on('click', function(e) {
        if (!confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
        }
    });
    
    // Add active class to current nav item
    var currentPath = window.location.pathname;
    $('.nav-link').each(function() {
        var href = $(this).attr('href');
        if (currentPath.indexOf(href) !== -1 && href !== '/') {
            $(this).addClass('active');
        }
    });
    
    // Table row click to view details
    $('table tbody tr').on('click', function(e) {
        if (!$(e.target).is('button, a, input')) {
            var link = $(this).find('a.btn-info, a.btn-primary').first();
            if (link.length) {
                window.location.href = link.attr('href');
            }
        }
    });
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Form validation
    $('form').on('submit', function() {
        var submitBtn = $(this).find('button[type="submit"]');
        submitBtn.prop('disabled', true);
        submitBtn.html('<span class="spinner-border spinner-border-sm me-2"></span>Processing...');
    });
});

// Utility Functions

// Format number to 2 decimal places
function formatNumber(num) {
    return parseFloat(num).toFixed(2);
}

// Get risk color based on value
function getRiskColor(value, inverse = false) {
    if (inverse) {
        // For attention - higher is better
        if (value >= 0.6) return 'success';
        if (value >= 0.4) return 'warning';
        return 'danger';
    } else {
        // For fatigue, stress, workload - lower is better
        if (value < 0.5) return 'success';
        if (value < 0.7) return 'warning';
        return 'danger';
    }
}

// Format timestamp
function formatTimestamp(date) {
    return new Date(date).toLocaleString();
}

// Show notification
function showNotification(message, type = 'info') {
    var alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('.container').first().prepend(alertHtml);
    
    setTimeout(function() {
        $('.alert').first().fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
}

// AJAX Error Handler
$(document).ajaxError(function(event, jqxhr, settings, thrownError) {
    console.error('AJAX Error:', thrownError);
    showNotification('An error occurred. Please try again.', 'danger');
});
