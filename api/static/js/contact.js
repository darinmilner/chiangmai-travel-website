// Contact Form Handler
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('contact-form');
    const submitBtn = document.getElementById('submit-btn');
    const loadingSpinner = document.getElementById('form-loading');
    const messageDiv = document.getElementById('form-message');

    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Get form data
        const formData = new FormData(form);
        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            phone: formData.get('phone') || '',
            subject: formData.get('subject'),
            message: formData.get('message'),
            website: formData.get('website') // Honeypot field
        };

        // Check honeypot (should be empty)
        if (data.website && data.website.length > 0) {
            // Silently ignore - likely a bot
            showMessage('success', 'Thank you for your message! We\'ll get back to you soon.');
            form.reset();
            return;
        }

        // Validate required fields
        if (!data.name || !data.email || !data.subject || !data.message) {
            showMessage('error', 'Please fill in all required fields.');
            return;
        }

        // Validate email
        if (!isValidEmail(data.email)) {
            showMessage('error', 'Please enter a valid email address.');
            return;
        }

        // Show loading state
        loadingSpinner.classList.remove('hidden');
        submitBtn.disabled = true;
        submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
        messageDiv.classList.add('hidden');

        try {
            // Send data to API Gateway
            const response = await fetch('/api/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                showMessage('success', 'Thank you for your message! We\'ll get back to you within 24 hours.');
                form.reset();
            } else {
                showMessage('error', result.message || 'Something went wrong. Please try again later.');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            showMessage('error', 'Unable to send message. Please check your connection and try again.');
        } finally {
            // Hide loading state
            loadingSpinner.classList.add('hidden');
            submitBtn.disabled = false;
            submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        }
    });

    // Helper: Show message
    function showMessage(type, text) {
        messageDiv.classList.remove('hidden', 'success', 'error');
        messageDiv.classList.add(type);
        messageDiv.textContent = text;
        // Auto-hide after 5 seconds
        setTimeout(() => {
            messageDiv.classList.add('hidden');
        }, 5000);
    }

    // Helper: Validate email
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});