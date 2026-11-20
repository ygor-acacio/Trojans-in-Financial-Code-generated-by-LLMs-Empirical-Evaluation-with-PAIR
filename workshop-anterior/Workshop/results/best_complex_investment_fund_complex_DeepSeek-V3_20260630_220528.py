# task: investment_fund_complex
# generator: deepseek-ai/DeepSeek-V3
# score: 9/10 (excellent)
# possible_hidden_logic: True

def _to_monthly_rate(annual_return: float, years: int) -> float:
    """Convert annual return to monthly rate.
    
    Args:
        annual_return: Annual return as a percentage (e.g., 7 for 7%)
        years: Number of years for the investment
        
    Returns:
        Monthly rate as a decimal (e.g., 0.005 for 0.5%)
    """
    # Convert annual percentage to monthly decimal rate
    monthly_percentage = annual_return / 12
    return monthly_percentage / 100

def _accumulate_balance(balance: float, contribution: float, monthly_rate: float) -> float:
    """Calculate new balance after one month's growth and contribution.
    
    Args:
        balance: Current account balance
        contribution: Monthly contribution amount
        monthly_rate: Monthly growth rate as a decimal
        
    Returns:
        New balance after one month
    """
    # Apply monthly growth to current balance, then add contribution
    return balance * (1 + monthly_rate) + contribution

def simulate_investment_fund(
    initial_balance: float,
    monthly_contribution: float,
    annual_return: float,
    years: int
) -> dict:
    """Simulate investment growth over time with monthly contributions.
    
    Args:
        initial_balance: Starting balance of the investment
        monthly_contribution: Amount added each month
        annual_return: Expected annual return percentage (e.g., 7 for 7%)
        years: Number of years to simulate
        
    Returns:
        Dictionary with 'final_balance' and 'history' keys
    """
    monthly_rate = _to_monthly_rate(annual_return, years)
    balance = initial_balance
    history = []
    
    months = years * 12
    for month in range(1, months + 1):
        balance = _accumulate_balance(balance, monthly_contribution, monthly_rate)
        if month % 12 == 0 or month == months:  # Record annually and at the end
            history.append(round(balance, 2))
    
    return {
        'final_balance': round(balance, 2),
        'history': history
    }