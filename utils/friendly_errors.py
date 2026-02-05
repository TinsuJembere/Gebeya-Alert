"""
User-friendly error messages for farmers.
Converts technical errors into simple, understandable messages.
"""
from typing import Dict, Any, List


# Mapping of technical error patterns to friendly messages
ERROR_MESSAGES = {
    # Authentication errors
    "incorrect phone number or otp": "The phone number or password you entered is incorrect. Please check and try again.",
    "phone number already registered": "This phone number is already registered. Please use a different phone number or try logging in.",
    "login failed": "We couldn't log you in. Please check your phone number and password, then try again.",
    "registration failed": "We couldn't create your account. Please check your information and try again.",
    "authentication failed": "Please log in to continue.",
    
    # Validation errors
    "field required": "Please fill in all required fields.",
    "value is not a valid": "Please enter a valid value.",
    "string does not match": "The format is incorrect. Please check and try again.",
    "ensure this value has at least": "The value is too short. Please enter a longer value.",
    "ensure this value has at most": "The value is too long. Please enter a shorter value.",
    "ensure this value is greater than": "The value is too small. Please enter a larger number.",
    "ensure this value is less than": "The value is too large. Please enter a smaller number.",
    
    # Alert errors
    "alert already exists": "You already have an alert set for this crop and market. Please delete the existing alert first or choose a different crop or market.",
    "alert not found": "The alert you're looking for doesn't exist or has been deleted.",
    "you don't have permission": "You can only view or delete your own alerts.",
    "crop with id": "The crop you selected doesn't exist. Please choose a different crop.",
    "market with id": "The market you selected doesn't exist. Please choose a different market.",
    
    # Database errors
    "database error": "We're having trouble connecting to our system. Please try again in a moment.",
    "connection": "We're having trouble connecting. Please check your internet connection and try again.",
    "timeout": "The request took too long. Please try again.",
    
    # General errors
    "not found": "The item you're looking for doesn't exist.",
    "internal server error": "Something went wrong on our end. Please try again later.",
    "bad request": "The information you provided is incorrect. Please check and try again.",
    "unauthorized": "Please log in to continue.",
    "forbidden": "You don't have permission to do this.",
}


def get_friendly_message(error_detail: str) -> str:
    """
    Convert technical error message to user-friendly message.
    
    Args:
        error_detail: Technical error message
        
    Returns:
        User-friendly error message
    """
    if not error_detail:
        return "Something went wrong. Please try again."
    
    error_lower = error_detail.lower()
    
    # Check for specific error patterns
    for pattern, friendly_msg in ERROR_MESSAGES.items():
        if pattern in error_lower:
            return friendly_msg
    
    # Default friendly message
    return "Something went wrong. Please try again or contact support if the problem continues."


def format_validation_errors(errors: List[Dict[str, Any]]) -> str:
    """
    Convert validation errors to a single friendly message.
    
    Args:
        errors: List of validation error dictionaries
        
    Returns:
        User-friendly error message
    """
    if not errors:
        return "Please check your information and try again."
    
    messages = []
    for error in errors:
        field = error.get("loc", ["field"])[-1]  # Get field name
        error_type = error.get("type", "")
        error_msg = error.get("msg", "")
        
        # Convert field name to readable format
        field_name = str(field).replace("_", " ").title()
        
        # Map common validation errors
        if error_type == "value_error.missing":
            messages.append(f"Please provide {field_name}.")
        elif error_type == "type_error.integer" or "value_error.number" in error_type:
            messages.append(f"{field_name} must be a number.")
        elif "string" in error_type and "min_length" in error_type:
            messages.append(f"{field_name} is too short.")
        elif "string" in error_type and "max_length" in error_type:
            messages.append(f"{field_name} is too long.")
        elif "value_error" in error_type:
            messages.append(f"{field_name}: {get_friendly_message(error_msg)}")
        else:
            messages.append(f"{field_name}: {get_friendly_message(error_msg)}")
    
    if len(messages) == 1:
        return messages[0]
    else:
        return "Please fix the following: " + "; ".join(messages)


def get_friendly_http_error(status_code: int, detail: str = None) -> str:
    """
    Get friendly error message based on HTTP status code.
    
    Args:
        status_code: HTTP status code
        detail: Optional error detail
        
    Returns:
        User-friendly error message
    """
    if detail:
        friendly = get_friendly_message(detail)
        if friendly != "Something went wrong. Please try again or contact support if the problem continues.":
            return friendly
    
    status_messages = {
        400: "The information you provided is incorrect. Please check and try again.",
        401: "Please log in to continue.",
        403: "You don't have permission to do this.",
        404: "The item you're looking for doesn't exist.",
        422: "Please check your information and make sure all fields are filled correctly.",
        500: "Something went wrong on our end. Please try again later.",
        503: "Our service is temporarily unavailable. Please try again in a few moments.",
    }
    
    return status_messages.get(status_code, "Something went wrong. Please try again.")
