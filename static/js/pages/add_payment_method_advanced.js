window.onload = function () {

const name = document.getElementById('name');
const cardnumber = document.getElementById('cardnumber');
const expirationdate = document.getElementById('expirationdate');
const securitycode = document.getElementById('securitycode');
const output = document.getElementById('output');
const ccicon = document.getElementById('ccicon');
const ccsingle = document.getElementById('ccsingle');
const generatecard = document.getElementById('generatecard');


let cctype = null;

//Mask the Credit Card Number Input
var cardnumber_mask = new IMask(cardnumber, {
    mask: [
        {
            mask: '0000 000000 00000',
            regex: '^3[47]\\d{0,13}',
            cardtype: 'american express'
        },
        {
            mask: '0000 0000 0000 0000',
            regex: '^(?:6011|65\\d{0,2}|64[4-9]\\d?)\\d{0,12}',
            cardtype: 'discover'
        },
        {
            mask: '0000 000000 0000',
            regex: '^3(?:0([0-5]|9)|[689]\\d?)\\d{0,11}',
            cardtype: 'diners'
        },
        {
            mask: '0000 0000 0000 0000',
            regex: '^(5[1-5]\\d{0,2}|22[2-9]\\d{0,1}|2[3-7]\\d{0,2})\\d{0,12}',
            cardtype: 'mastercard'
        },
        {
            mask: '0000 000000 00000',
            regex: '^(?:2131|1800)\\d{0,11}',
            cardtype: 'jcb15'
        },
        {
            mask: '0000 0000 0000 0000',
            regex: '^(?:35\\d{0,2})\\d{0,12}',
            cardtype: 'jcb'
        },
        {
            mask: '0000 0000 0000 0000',
            regex: '^(?:5[0678]\\d{0,2}|6304|67\\d{0,2})\\d{0,12}',
            cardtype: 'maestro'
        },
        {
            mask: '0000 0000 0000 0000',
            regex: '^4\\d{0,15}',
            cardtype: 'visa'
        },
        {
            mask: '0000 0000 0000 0000',
            regex: '^62\\d{0,14}',
            cardtype: 'unionpay'
        },
        {
            mask: '0000 0000 0000 0000',
            regex: '^6[0-9]\\d{0,13}',
            cardtype: 'rupay'
        },
        {
            mask: '0000 0000 0000 0000',
            regex: '^9[0-9]\\d{0,13}',
            cardtype: 'indian_bank'
        },
        {
            mask: '0000 0000 0000 0000',
            cardtype: 'Unknown'
        }
    ],
    dispatch: function (appended, dynamicMasked) {
        var number = (dynamicMasked.value + appended).replace(/\D/g, '');

        for (var i = 0; i < dynamicMasked.compiledMasks.length; i++) {
            let re = new RegExp(dynamicMasked.compiledMasks[i].regex);
            if (number.match(re) != null) {
                return dynamicMasked.compiledMasks[i];
            }
        }
    }
});

//Mask the Expiration Date
var expirationdate_mask = new IMask(expirationdate, {
    mask: 'MM{/}YY',
    groups: {
        YY: new IMask.MaskedPattern.Group.Range([0, 99]),
        MM: new IMask.MaskedPattern.Group.Range([1, 12]),
    },
    lazy: false,
    placeholderChar: '_'
});

//Mask the security code
var securitycode_mask = new IMask(securitycode, {
    mask: '0000',
});

//define the color swap function
const swapColor = function (basecolor) {
    document.querySelectorAll('.lightcolor')
        .forEach(function (input) {
            input.setAttribute('class', '');
            input.setAttribute('class', 'lightcolor ' + basecolor);
        });
    document.querySelectorAll('.darkcolor')
        .forEach(function (input) {
            input.setAttribute('class', '');
            input.setAttribute('class', 'darkcolor ' + basecolor + 'dark');
        });
};

//pop in the appropriate card icon when detected
cardnumber_mask.on("accept", function () {
    switch (cardnumber_mask.masked.currentMask.cardtype) {
        case 'american express':
            swapColor('green');
            break;
        case 'visa':
            swapColor('lime');
            break;
        case 'diners':
            swapColor('orange');
            break;
        case 'discover':
            swapColor('purple');
            break;
        case ('jcb' || 'jcb15'):
            swapColor('red');
            break;
        case 'maestro':
            swapColor('yellow');
            break;
        case 'mastercard':
            swapColor('lightblue');
            break;
        case 'unionpay':
            swapColor('cyan');
            break;
        case 'rupay':
            swapColor('purple');
            break;
        case 'indian_bank':
            swapColor('orange');
            break;
        default:
            swapColor('grey');
            break;
    }
});

//Generate random card number from list of known test numbers
const randomCard = function () {
    let testCards = [
        '4000056655665556', // Visa
        '5200828282828210', // Mastercard
        '371449635398431',  // Amex
        '6011000990139424', // Discover
        '30569309025904',   // Diners
        '3566002020360505', // JCB
        '6200000000000005', // UnionPay
        '6759649826438453', // Maestro
        '6073849700000000', // RuPay
        '6073849700000001', // RuPay
        '9500000000000000', // Indian Bank
        '9500000000000001', // Indian Bank
    ];
    let randomNumber = Math.floor(Math.random() * testCards.length);
    cardnumber_mask.unmaskedValue = testCards[randomNumber];
}
generatecard.addEventListener('click', function () {
    randomCard();
});

// CREDIT CARD IMAGE JS
document.querySelector('.preload').classList.remove('preload');
document.querySelector('.creditcard').addEventListener('click', function () {
    if (this.classList.contains('flipped')) {
        this.classList.remove('flipped');
    } else {
        this.classList.add('flipped');
    }
})

//On Input Change Events
name.addEventListener('input', function () {
    if (name.value.length == 0) {
        document.getElementById('svgname').innerHTML = 'John Doe';
        document.getElementById('svgnameback').innerHTML = 'John Doe';
    } else {
        document.getElementById('svgname').innerHTML = this.value;
        document.getElementById('svgnameback').innerHTML = this.value;
    }
});

cardnumber_mask.on('accept', function () {
    if (cardnumber_mask.value.length == 0) {
        document.getElementById('svgnumber').innerHTML = '0123 4567 8910 1112';
    } else {
        document.getElementById('svgnumber').innerHTML = cardnumber_mask.value;
    }
});

expirationdate_mask.on('accept', function () {
    if (expirationdate_mask.value.length == 0) {
        document.getElementById('svgexpire').innerHTML = '01/23';
    } else {
        document.getElementById('svgexpire').innerHTML = expirationdate_mask.value;
    }
});

securitycode_mask.on('accept', function () {
    if (securitycode_mask.value.length == 0) {
        document.getElementById('svgsecurity').innerHTML = '985';
    } else {
        document.getElementById('svgsecurity').innerHTML = securitycode_mask.value;
    }
});

//On Focus Events
name.addEventListener('focus', function () {
    document.querySelector('.creditcard').classList.remove('flipped');
});

cardnumber.addEventListener('focus', function () {
    document.querySelector('.creditcard').classList.remove('flipped');
});

expirationdate.addEventListener('focus', function () {
    document.querySelector('.creditcard').classList.remove('flipped');
});

securitycode.addEventListener('focus', function () {
    document.querySelector('.creditcard').classList.add('flipped');
});

// Form submission
const form = document.querySelector('form');
const addCardBtn = document.querySelector('#addPaymentMethodBtn');

console.log('Form element:', form);
console.log('Submit button:', addCardBtn);
console.log('Form method:', form ? form.method : 'NOT FOUND');
console.log('Form action:', form ? form.action : 'NOT FOUND');

if (addCardBtn) {
    // Completely disable form submission
    if (form) {
        form.onsubmit = function(e) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            console.log('Form submission completely blocked!');
            return false;
        };
        
        // Also prevent any form submission events
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            console.log('Form submit event blocked!');
            return false;
        });
    }
    
    // Handle everything through button click
    addCardBtn.addEventListener('click', async function(e) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();
        
        console.log('Button clicked - handling payment method addition!');
        showInfoToast('Form submitted! Check console for details.');
        console.log('Form submitted!');
        
        // Get form data
        const cardNumber = cardnumber_mask.unmaskedValue;
        const cardType = cardnumber_mask.masked.currentMask ? cardnumber_mask.masked.currentMask.cardtype : 'Unknown';
        const expiryDate = expirationdate_mask.value;
        const securityCode = securitycode_mask.value;
        const cardholderName = name.value.trim();
        
        console.log('Form data:', {
            cardNumber: cardNumber,
            cardType: cardType,
            expiryDate: expiryDate,
            securityCode: securityCode,
            cardholderName: cardholderName
        });
        
        // Step 1: Validate form
        console.log('Step 1: Validating form...');
        if (!cardNumber || cardNumber.length < 13) {
            showErrorToast('Please enter a valid card number');
            return;
        }
        
        if (!expiryDate || expiryDate.length !== 5) {
            showErrorToast('Please enter a valid expiry date (MM/YY)');
            return;
        }
        
        if (!securityCode || securityCode.length < 3) {
            showErrorToast('Please enter a valid security code');
            return;
        }
        
        if (!cardholderName) {
            showErrorToast('Please enter the cardholder name');
            return;
        }
        
        // Step 2: Process data
        console.log('Step 2: Processing form data...');
        
        // Extract last 4 digits and expiry
        const lastFourDigits = cardNumber.slice(-4);
        const [expiryMonth, expiryYear] = expiryDate.split('/');
        const fullExpiryYear = '20' + expiryYear;
        
        // Map card types to database values
        const cardTypeMap = {
            'visa': 'VISA',
            'mastercard': 'MASTERCARD',
            'american express': 'AMERICAN_EXPRESS',
            'discover': 'DISCOVER',
            'diners': 'DINERS_CLUB',
            'jcb': 'JCB',
            'jcb15': 'JCB',
            'maestro': 'MASTERCARD',
            'unionpay': 'VISA',
            'rupay': 'VISA',
            'indian_bank': 'VISA',
            'Unknown': 'VISA'
        };
        
        const dbCardType = cardTypeMap[cardType.toLowerCase()] || 'VISA';
        
        // Prepare data for API
        const paymentData = {
            payment_type: 'CREDIT_CARD',
            card_type: dbCardType,
            last_four_digits: lastFourDigits,
            expiry_month: expiryMonth,
            expiry_year: fullExpiryYear,
            cardholder_name: cardholderName,
            is_default: true
        };
        
        console.log('Payment data to send:', paymentData);
        console.log('JSON stringified data:', JSON.stringify(paymentData));
        
        // Step 3: Show loading state
        console.log('Step 3: Showing loading state...');
        
        // Show loading state
        addCardBtn.disabled = true;
        addCardBtn.textContent = 'Adding Card...';
        
        try {
            console.log('Step 4: Making API call...');
            console.log('Sending request to /api/payment-methods/add/');
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            console.log('CSRF Token element:', csrfToken);
            console.log('CSRF Token value:', csrfToken ? csrfToken.value : 'NOT FOUND');
            
            const response = await fetch('/api/payment-methods/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken ? csrfToken.value : ''
                },
                body: JSON.stringify(paymentData)
            });
            
            console.log('Request headers sent:', {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken ? csrfToken.value : ''
            });
            
            console.log('Request body being sent:', JSON.stringify(paymentData));
            
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Error response:', errorText);
                showErrorToast('API Error: ' + response.status + ' - ' + errorText);
                return;
            }
            
            const result = await response.json();
            console.log('Response data:', result);
            
            if (result.success) {
                // Show success message and update button
                addCardBtn.textContent = '✓ Payment Method Added!';
                addCardBtn.classList.remove('btn-primary');
                addCardBtn.classList.add('btn-success');
                
                showSuccessToast(`Payment method added successfully!\n\nCard: ${result.payment_method.display_name}\nExpires: ${result.payment_method.expiry_display}\n\nRedirecting to billing page...`);
                console.log('SUCCESS: Payment method created with ID:', result.payment_method.id);
                
                // Redirect to billing page after successful addition
                setTimeout(() => {
                    window.location.href = '/company/billing-subscriptions/';
                }, 2000); // Wait 2 seconds to show the success message
                
                return; // Don't reset form since we're redirecting
            } else {
                showErrorToast('Error: ' + result.error);
            }
        } catch (error) {
            console.error('Error:', error);
            showErrorToast('An error occurred while adding the payment method');
        } finally {
            // Reset button state
            addCardBtn.disabled = false;
            addCardBtn.textContent = 'Add Payment Method';
        }
    });
}
};
