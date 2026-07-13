import re
from typing import Dict, Any, Tuple, Optional

# Optional: Use email-validator library
try:
    from email_validator import validate_email, EmailNotValidError
    USE_EMAIL_VALIDATOR = True
except ImportError:
    USE_EMAIL_VALIDATOR = False

class ContactFormValidator:
    """Validate and sanitize contact form inputs"""

    # Constants
    MAX_NAME_LENGTH = 100
    MIN_NAME_LENGTH = 2
    MAX_MESSAGE_LENGTH = 5000
    MIN_MESSAGE_LENGTH = 10
    MAX_SUBJECT_LENGTH = 200
    MIN_SUBJECT_LENGTH = 3

    # XSS patterns to block
    XSS_PATTERNS = [
        r'<script', r'javascript:', r'on\w+=', r'data:text/html',
        r'<iframe', r'<embed', r'<object', r'<meta', r'<link'
    ]

    @classmethod
    def validate_email_address(cls, email: str) -> Tuple[bool, str]:
        """
        Validate email address format

        Returns:
            (is_valid, normalized_email_or_error_message)
        """
        if not email or not isinstance(email, str):
            return False, "Email is required"

        email = email.strip()

        if len(email) > 254:  # RFC 5321 max length
            return False, "Email address is too long"

        if USE_EMAIL_VALIDATOR:
            try:
                validated = validate_email(email)
                return True, validated.email
            except EmailNotValidError as e:
                return False, str(e)
        else:
            # Fallback to basic regex validation
            # RFC 5322 compliant pattern (simplified)
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(pattern, email):
                return True, email
            return False, "Invalid email address format"

    @classmethod
    def validate_name(cls, name: str) -> Tuple[bool, str]:
        """
        Validate name field

        Returns:
            (is_valid, sanitized_name_or_error_message)
        """
        if not name or not isinstance(name, str):
            return False, "Name is required"

        name = name.strip()

        if len(name) < cls.MIN_NAME_LENGTH:
            return False, f"Name must be at least {cls.MIN_NAME_LENGTH} characters"

        if len(name) > cls.MAX_NAME_LENGTH:
            return False, f"Name must be less than {cls.MAX_NAME_LENGTH} characters"

        # Check for XSS patterns
        if cls._contains_xss(name):
            return False, "Name contains invalid characters"

        # Prevent excessive whitespace
        if re.search(r'\s{3,}', name):
            return False, "Name contains excessive whitespace"

        # Allow common name characters
        if not re.match(r'^[a-zA-Z\s\-\.\'à-ÿÀ-Ÿ]+$', name):
            # Still allow if it's just some special characters
            # But don't allow HTML tags
            if re.search(r'<[^>]+>', name):
                return False, "Name contains HTML tags"

        # Capitalize first letter of each word
        name = ' '.join(word.capitalize() for word in name.split())

        return True, name

    @classmethod
    def validate_message(cls, message: str) -> Tuple[bool, str]:
        """
        Validate message field

        Returns:
            (is_valid, sanitized_message_or_error_message)
        """
        if not message or not isinstance(message, str):
            return False, "Message is required"

        message = message.strip()

        if len(message) < cls.MIN_MESSAGE_LENGTH:
            return False, f"Message must be at least {cls.MIN_MESSAGE_LENGTH} characters"

        if len(message) > cls.MAX_MESSAGE_LENGTH:
            return False, f"Message must be less than {cls.MAX_MESSAGE_LENGTH} characters"

        # Check for XSS patterns
        if cls._contains_xss(message):
            return False, "Message contains invalid content"

        # Check for SQL injection patterns (basic)
        sql_patterns = [r' UNION ', r'SELECT.*FROM', r'DROP TABLE', r'DELETE FROM']
        for pattern in sql_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return False, "Message contains invalid SQL patterns"

        # Normalize whitespace (collapse multiple spaces)
        message = re.sub(r'\s+', ' ', message)

        return True, message

    @classmethod
    def validate_subject(cls, subject: str) -> Tuple[bool, str]:
        """
        Validate subject field

        Returns:
            (is_valid, sanitized_subject_or_error_message)
        """
        if not subject or not isinstance(subject, str):
            return False, "Subject is required"

        subject = subject.strip()

        if len(subject) < cls.MIN_SUBJECT_LENGTH:
            return False, f"Subject must be at least {cls.MIN_SUBJECT_LENGTH} characters"

        if len(subject) > cls.MAX_SUBJECT_LENGTH:
            return False, f"Subject must be less than {cls.MAX_SUBJECT_LENGTH} characters"

        # Check for XSS patterns
        if cls._contains_xss(subject):
            return False, "Subject contains invalid characters"

        # Remove excessive punctuation
        subject = re.sub(r'[!?.,]{3,}', '...', subject)

        return True, subject

    @classmethod
    def _contains_xss(cls, text: str) -> bool:
        """Check if text contains XSS patterns"""
        text_lower = text.lower()
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        return False

    @classmethod
    def validate_all(cls, data: Dict[str, Any]) -> Tuple[bool, Dict[str, str], Dict[str, Any]]:
        """
        Validate all form fields

        Args:
            data: Raw form data dict

        Returns:
            (is_valid, errors, cleaned_data)
        """
        errors = {}
        cleaned = {}

        # Validate each field
        is_valid, result = cls.validate_email_address(data.get('email', ''))
        if is_valid:
            cleaned['email'] = result
        else:
            errors['email'] = result

        is_valid, result = cls.validate_name(data.get('name', ''))
        if is_valid:
            cleaned['name'] = result
        else:
            errors['name'] = result

        is_valid, result = cls.validate_subject(data.get('subject', ''))
        if is_valid:
            cleaned['subject'] = result
        else:
            errors['subject'] = result

        is_valid, result = cls.validate_message(data.get('message', ''))
        if is_valid:
            cleaned['message'] = result
        else:
            errors['message'] = result

        # Add IP address if provided (for logging)
        if 'ip' in data:
            cleaned['ip'] = data['ip']

        return len(errors) == 0, errors, cleaned