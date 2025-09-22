// Simple Animation Test
console.log('Animation test script loaded');

window.onload = function() {
    console.log('Animation test window.onload executed');
    
    // Wait for everything to load
    setTimeout(() => {
        const creditCard = document.querySelector('.creditcard');
        const container = document.querySelector('.container');
        
        if (creditCard && container) {
            console.log('Found credit card and container elements');
            console.log('Container perspective:', window.getComputedStyle(container).perspective);
            console.log('Credit card transition:', window.getComputedStyle(creditCard).transition);
            console.log('Credit card transform-style:', window.getComputedStyle(creditCard).transformStyle);
            
            // Add simple click handler
            creditCard.addEventListener('click', function() {
                console.log('Card clicked!');
                if (this.classList.contains('flipped')) {
                    this.classList.remove('flipped');
                    console.log('Removed flipped class');
                } else {
                    this.classList.add('flipped');
                    console.log('Added flipped class');
                }
            });
            
            // Test with inline styles
            setTimeout(() => {
                console.log('Testing with inline styles...');
                creditCard.style.transition = 'transform 0.6s ease-in-out';
                creditCard.style.transformStyle = 'preserve-3d';
                creditCard.classList.add('flipped');
                console.log('Added flipped class with inline styles');
                
                setTimeout(() => {
                    creditCard.classList.remove('flipped');
                    console.log('Removed flipped class');
                }, 1000);
            }, 2000);
            
        } else {
            console.error('Credit card or container not found');
            console.log('Available elements:', document.querySelectorAll('*'));
        }
    }, 1000);
};
