"""
Input validation and security utilities
"""
import re
from typing import List, Dict, Any
from urllib.parse import urlparse


class InputValidator:
    """Validates user inputs to prevent injection attacks"""

    @staticmethod
    def validate_domain(domain: str) -> bool:
        """
        Validate domain name format
        """
        # Remove protocol if present
        domain = domain.replace('https://', '').replace('http://', '')

        # Domain regex
        pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return bool(re.match(pattern, domain))

    @staticmethod
    def validate_target(target: str) -> Dict[str, Any]:
        """
        Validate and normalize target
        Returns dict with validation result
        """
        if not target or len(target) > 253:
            return {'valid': False, 'error': 'Invalid target length'}

        # Check for dangerous characters
        dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '<', '>', '\n', '\r']
        if any(char in target for char in dangerous_chars):
            return {'valid': False, 'error': 'Target contains dangerous characters'}

        # Try to parse as domain
        cleaned_target = target.replace('https://', '').replace('http://', '').split('/')[0]

        # Check if it's a valid domain or IP
        if InputValidator.validate_domain(cleaned_target) or InputValidator.validate_ip(cleaned_target):
            return {
                'valid': True,
                'normalized': cleaned_target,
                'type': 'ip' if InputValidator.validate_ip(cleaned_target) else 'domain'
            }

        return {'valid': False, 'error': 'Invalid domain or IP format'}

    @staticmethod
    def validate_ip(ip: str) -> bool:
        """Validate IPv4 address"""
        pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return bool(re.match(pattern, ip))

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal
        """
        # Remove any path components
        filename = filename.replace('../', '').replace('..\\', '')

        # Allow only alphanumeric, dash, underscore, and dot
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

        return filename

    @staticmethod
    def validate_file_path(path: str, allowed_base: str = '/opt/results') -> bool:
        """
        Validate file path is within allowed directory
        Prevents path traversal attacks
        """
        import os

        # Normalize paths
        abs_path = os.path.abspath(path)
        abs_base = os.path.abspath(allowed_base)

        # Check if path is within base
        return abs_path.startswith(abs_base)

    @staticmethod
    def sanitize_user_id(user_id: str) -> str:
        """Sanitize user ID"""
        # Allow only alphanumeric, dash, and underscore
        return re.sub(r'[^a-zA-Z0-9_-]', '', user_id)[:100]

    @staticmethod
    def validate_tool_arguments(args: List[str]) -> bool:
        """
        Validate tool arguments to prevent command injection
        """
        dangerous_patterns = [
            r';\s*',  # Command chaining with semicolon
            r'\|\s*',  # Pipe
            r'&\s*&',  # AND
            r'\$\(',  # Command substitution
            r'`',  # Backticks
            r'>\s*',  # Redirect
            r'<\s*',  # Redirect
        ]

        for arg in args:
            for pattern in dangerous_patterns:
                if re.search(pattern, arg):
                    return False

        return True


class RateLimiter:
    """Simple rate limiter"""

    def __init__(self):
        self.requests = {}

    def check_rate_limit(self, key: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
        """
        Check if request is within rate limit
        Returns True if allowed, False if rate limited
        """
        import time

        now = time.time()

        if key not in self.requests:
            self.requests[key] = []

        # Clean old requests
        self.requests[key] = [t for t in self.requests[key] if now - t < window_seconds]

        # Check limit
        if len(self.requests[key]) >= max_requests:
            return False

        # Add current request
        self.requests[key].append(now)

        return True


# Global rate limiter instance
_rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter"""
    return _rate_limiter
