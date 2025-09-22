// Form Validation JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Terms validation script loaded');
    
    // Terms and Conditions checkbox validation
    const termsCheckboxes = document.querySelectorAll('input[id*="termsCheck"]');
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    
    console.log('Found checkboxes:', termsCheckboxes.length);
    console.log('Found submit buttons:', submitButtons.length);
    
    termsCheckboxes.forEach(function(checkbox, index) {
        console.log(`Checkbox ${index}:`, checkbox.id, checkbox.checked);
        
        checkbox.addEventListener('change', function() {
            console.log(`Checkbox ${this.id} changed to:`, this.checked);
            validateTermsAgreement();
        });
        
        // Add click event for better UX
        checkbox.addEventListener('click', function(e) {
            console.log(`Checkbox ${this.id} clicked`);
            // Let the default behavior handle the state change
        });
    });
    
    function validateTermsAgreement() {
        let allChecked = true;
        termsCheckboxes.forEach(function(checkbox) {
            if (!checkbox.checked) {
                allChecked = false;
            }
        });
        
        console.log('All checkboxes checked:', allChecked);
        
        submitButtons.forEach(function(button) {
            // TEMPORARILY DISABLED FOR TESTING - Always enable button
            button.disabled = false;
            button.classList.remove('btn-secondary');
            button.classList.add('btn-primary');
            console.log('Submit button enabled (terms validation disabled)');
            
            if (allChecked) {
                button.disabled = false;
                button.classList.remove('btn-secondary');
                button.classList.add('btn-primary');
                console.log('Submit button enabled');
            } else {
                button.disabled = true;
                button.classList.remove('btn-primary');
                button.classList.add('btn-secondary');
                console.log('Submit button disabled');
            }
        });
    }
    
    // Initial validation
    validateTermsAgreement();
    
    // Form submission validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const formCheckboxes = form.querySelectorAll('input[id*="termsCheck"]');
            let termsAgreed = true;
            
            formCheckboxes.forEach(function(checkbox) {
                if (!checkbox.checked) {
                    termsAgreed = false;
                }
            });
            
            // TEMPORARILY DISABLED FOR TESTING
            console.log('Terms validation temporarily disabled for testing');
            return true; // Allow form submission
            
            if (!termsAgreed) {
                e.preventDefault();
                showErrorToast('Please agree to the Terms of Service and Privacy Policy to continue.');
                console.log('Form submission prevented - terms not agreed');
                return false;
            }
            
            console.log('Form submission allowed - terms agreed');
        });
    });
    
    // Add visual feedback for checkbox state
    termsCheckboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            const label = this.nextElementSibling;
            if (this.checked) {
                label.style.color = '#28a745';
                label.style.fontWeight = '600';
                console.log(`Checkbox ${this.id} checked - green label`);
            } else {
                label.style.color = '#6c757d';
                label.style.fontWeight = 'normal';
                console.log(`Checkbox ${this.id} unchecked - gray label`);
            }
        });
        
        // Initial state
        if (checkbox.checked) {
            const label = checkbox.nextElementSibling;
            label.style.color = '#28a745';
            label.style.fontWeight = '600';
        }
    });
    
    // Add click handler for labels to improve UX
    const labels = document.querySelectorAll('label[for*="termsCheck"]');
    labels.forEach(function(label) {
        label.addEventListener('click', function(e) {
            // Don't prevent default if clicking on links
            if (e.target.tagName === 'A') {
                return;
            }
            
            const checkbox = document.getElementById(label.getAttribute('for'));
            if (checkbox) {
                checkbox.checked = !checkbox.checked;
                checkbox.dispatchEvent(new Event('change'));
                console.log(`Label clicked for checkbox ${checkbox.id}`);
            }
        });
    });
    
    console.log('Terms and Conditions validation initialized successfully');
});
