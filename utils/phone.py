"""
Phone number utility functions.
"""
import re
from typing import Optional


def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number to +251 format.
    
    Handles various formats:
    - +251911234567
    - 251911234567
    - 0911234567
    - 911234567
    
    Args:
        phone: Phone number in any format
        
    Returns:
        Normalized phone number in +251 format (e.g., +251911234567)
        
    Raises:
        ValueError: If phone number format is invalid
    """
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Remove leading + if present
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    # Handle different formats
    if cleaned.startswith('251'):
        # Already has country code
        normalized = f"+{cleaned}"
    elif cleaned.startswith('0'):
        # Remove leading 0 and add country code
        normalized = f"+251{cleaned[1:]}"
    elif len(cleaned) == 9:
        # 9 digits, assume it's local format (no leading 0)
        normalized = f"+251{cleaned}"
    else:
        raise ValueError(f"Invalid phone number format: {phone}")
    
    # Validate length (should be +251 + 9 digits = 13 characters total)
    if len(normalized) != 13 or not normalized.startswith('+251'):
        raise ValueError(f"Invalid phone number format: {phone}")
    
    # Validate that remaining digits are valid (should be 9 digits)
    digits = normalized[4:]  # Everything after +251
    if not digits.isdigit() or len(digits) != 9:
        raise ValueError(f"Invalid phone number format: {phone}")
    
    return normalized


def validate_phone_number(phone: str) -> bool:
    """
    Validate if phone number is in correct format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        normalize_phone_number(phone)
        return True
    except ValueError:
        return False
















