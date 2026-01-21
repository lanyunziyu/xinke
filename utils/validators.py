"""
Input validation utilities.
"""
from typing import Dict, Any, List


def validate_user_input(user_profile: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate user input profile.

    Args:
        user_profile: User profile dictionary

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check required fields
    required_fields = [
        "identity_info",
        "residence_status",
        "purchase_needs",
        "budget",
    ]

    for field in required_fields:
        if field not in user_profile:
            errors.append(f"Missing required field: {field}")

    # Validate budget
    if "budget" in user_profile:
        budget = user_profile["budget"]
        if not isinstance(budget, (int, float)) or budget <= 0:
            errors.append("Budget must be a positive number")

    # TODO: Add more validation rules

    is_valid = len(errors) == 0
    return is_valid, errors


def validate_location(location: str) -> bool:
    """
    Validate if location is a valid Beijing district.

    Args:
        location: Location/district name

    Returns:
        True if valid, False otherwise
    """
    valid_districts = [
        "东城", "西城", "朝阳", "海淀", "丰台", "石景山",
        "通州", "顺义", "昌平", "大兴", "房山", "门头沟",
        "平谷", "怀柔", "密云", "延庆"
    ]

    return location in valid_districts
