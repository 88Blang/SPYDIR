import numpy as np
import pandas as pd

pct_suffix = ("pct", "yield", "return", "growth", "margin", "roe", "roi", "roa")
cap_keys = ["ebitda", "ebit", "pe", "ps", "pb", "cad", "usd", "roe", "roa", "roi"]
pct_keys = ["pct"]


def format_number(number):
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
        return f"{number:.2f}"


def remove_number(formatted):
    """Converts a formatted string like '10 B' or '5.4 M' back into a float.

    Parameters:
        formatted (str): The formatted string.

    Returns:
        float or None: The numeric value, or None if parsing fails.
    """
    if not isinstance(formatted, str):
        return None

    formatted = formatted.strip().upper().replace(",", "")

    try:
        if formatted.endswith("B"):
            return float(formatted[:-1]) * 1e9
        elif formatted.endswith("M"):
            return float(formatted[:-1]) * 1e6
        else:
            return float(formatted)
    except ValueError:
        return None


def add_format(x):
    """Format a Series as percentage, currency, or number based on its name."""

    try:
        x = pd.to_numeric(x)
        is_numeric = True
    except Exception:
        is_numeric = False

    if not is_numeric:
        return x.map(lambda v: v)

    name_lower = x.name.lower()

    if name_lower.endswith(pct_suffix) or name_lower.startswith(pct_suffix):
        return x.map(format_pct)
    elif name_lower.endswith("price"):
        return x.map(format_currency)
    else:
        return x.map(format_number)


def remove_format(x):
    """Format a Series as percentage, currency, or number based on its name."""
    test = x.loc[0]

    if "%" in test:
        return x.map(remove_pct)
    elif "$" in test:
        return x.map(remove_currency)
    elif any(c.isalpha() for c in test) and not test.endswith(("M", "B")):
        return x
    else:
        return x.map(remove_number)


def remove_currency(x: str) -> int:
    """Convert string '$303,303,000' to integer 303303000 ."""
    if x in ["", "-", "--"]:
        return 0
    num = float(x.replace("$", "").replace(",", "").strip())
    return num


def format_currency(n: int) -> str:
    """Convert integer 303303000 to string like '$303,303,000'."""
    return f"${n:,.2f}"


def remove_pct(x: str) -> float:
    """Convert string 10.0% to float like '0.1'."""
    num = float(x.replace("%", "").replace(",", "").strip())
    return num / 100


def format_pct(n: float) -> str:
    """Convert float like '0.1' to string like '10.0%'."""
    return f"{n*100:,.2f}%"


def format_title(x):
    xs = x.lower().split("_")
    if len(xs) > 1:
        xl = []
        for xi in xs:
            xi = format_title(xi)

            xl.append(xi)
        xf = " ".join(xl)
        return xf
    if x in cap_keys:
        return x.upper()
    elif x in pct_keys:
        return "(%)"
    else:
        return x.title()
