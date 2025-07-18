"""
Currency formatting utilities
"""

from config.settings import CURRENCY_SYMBOL, CURRENCY_FORMAT


def format_currency(amount, symbol=None, decimal_places=2):
    """
    Format amount as currency with proper symbol and formatting
    
    Args:
        amount (float): The amount to format
        symbol (str): Currency symbol (defaults to CURRENCY_SYMBOL from settings)
        decimal_places (int): Number of decimal places (default: 2)
    
    Returns:
        str: Formatted currency string
    """
    if symbol is None:
        symbol = CURRENCY_SYMBOL
    
    if amount is None:
        amount = 0
    
    try:
        # Convert to float if it's not already
        amount = float(amount)
        
        # Format with decimal places
        if decimal_places == 0:
            formatted_amount = f"{amount:,.0f}"
        else:
            formatted_amount = f"{amount:,.{decimal_places}f}"
        
        return f"{symbol} {formatted_amount}"
    
    except (ValueError, TypeError):
        return f"{symbol} 0.00"


def format_currency_no_decimal(amount, symbol=None):
    """
    Format currency without decimal places
    
    Args:
        amount (float): The amount to format
        symbol (str): Currency symbol (defaults to CURRENCY_SYMBOL from settings)
    
    Returns:
        str: Formatted currency string without decimals
    """
    return format_currency(amount, symbol, decimal_places=0)


def parse_currency_input(input_str):
    """
    Parse currency input string to float value
    
    Args:
        input_str (str): Currency string like "Rs. 1,234.56" or "1234.56"
    
    Returns:
        float: Parsed amount or 0.0 if parsing fails
    """
    if not input_str:
        return 0.0
    
    try:
        # Remove currency symbol and whitespace
        cleaned = input_str.replace(CURRENCY_SYMBOL, "").strip()
        # Remove commas
        cleaned = cleaned.replace(",", "")
        # Convert to float
        return float(cleaned)
    except (ValueError, TypeError):
        return 0.0


def get_currency_symbol():
    """
    Get the current currency symbol
    
    Returns:
        str: Currency symbol
    """
    return CURRENCY_SYMBOL
