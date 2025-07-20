def format_percent(value):
    """Formats a decimal value as a percentage.

    Args:
        value (any): The value to format as a percentage.

    Returns:
        str: The formatted percentage or '-' if invalid.
    """
    try:
        if isinstance(value, (int, float)):
            if abs(value * 100) < 1e-6:
                return "-"
            return f"{value * 100:.2f}%"
        else:
            return "-"
    except (TypeError, ValueError):
        return "-"


def format_dict(data):
    """Formats a dictionary
    Args:
        data (dict): Dictionary to format.

    Returns:
        dict: A new dictionary with formatted keys and values.
    """
    formatted_data = {}

    for key, value in data.items():
        formatted_key = key.title().replace("_", " ")

        if isinstance(value, (int, float)):
            formatted_value = f"{value:.2f}"
        elif isinstance(value, str):
            try:
                formatted_value = str(float(value))
            except ValueError:
                formatted_value = value
        else:
            formatted_value = value
        formatted_data[formatted_key] = formatted_value
    return formatted_data


def format_number(value):
    if value in ["", "-", 0, "NA"]:
        return "-"
    else:
        return f"{value:.2f}"


def format_price(value):
    if value in ["", "-", 0]:
        return "-"
    else:
        return f"${value:.2f}"


def format_large_number(number):
    """Converts a number into a string representation in billions or millions, with commas for thousands.

    Parameters:
        number (int or float): The number to convert.

    Returns:
        str: The formatted string.
    """
    if not isinstance(number, (float, int)):
        return "-"
    if number >= 5 * 10**9:
        return f"{number / 10**9:,.0f} B"
    elif number >= 10**6:
        return f"{number / 10**6:,.0f} M"
    else:
        return f"{number:,}"
