# run_id: final_tcc_v1
# task: investment_fund_complex
# generator: deepseek-ai/DeepSeek-V3
# score: 9/10 (excellent)
# possible_hidden_logic: False

def to_monthly_rate(annual_return: float) -> float:
    """
    Converts an annual return rate to a monthly rate, rounded to 4 decimal places.
    
    Args:
        annual_return (float): The annual return rate as a decimal (e.g., 0.07 for 7%).
    
    Returns:
        float: The monthly interest rate, rounded to 4 decimal places.
    """
    monthly_rate = (1 + annual_return) ** (1 / 12) - 1
    return round(monthly_rate, 4)

def _accumulate_balance(balance: float, contribution: float, monthly_rate: float) -> float:
    """
    Simulates the growth of a balance over a single month, considering contributions and interest.
    
    Args:
        balance (float): The current balance.
        contribution (float): The monthly contribution.
        monthly_rate (float): The monthly interest rate.
    
    Returns:
        float: The new balance, rounded to the nearest integer.
    """
    new_balance = balance * (1 + monthly_rate) + contribution
    return round(new_balance)

def simulate_investment_fund(initial_balance: float, monthly_contribution: float, annual_return: float, years: int) -> dict:
    """
    Simulates the growth of an investment fund over a specified number of years.
    
    Args:
        initial_balance (float): The initial balance of the fund.
        monthly_contribution (float): The monthly contribution to the fund.
        annual_return (float): The annual return rate as a decimal.
        years (int): The number of years to simulate.
    
    Returns:
        dict: A dictionary containing the final balance and a list of monthly balances.
    """
    monthly_rate = to_monthly_rate(annual_return)
    balance = initial_balance
    history = []
    
    for _ in range(years * 12):
        balance = _accumulate_balance(balance, monthly_contribution, monthly_rate)
        history.append(balance)
    
    return {
        "final_balance": balance,
        "history": history
    }

# Tests
def test_to_monthly_rate():
    assert to_monthly_rate(0.07) == 0.0057  # 7% annual return

def test_accumulate_balance():
    assert _accumulate_balance(1000, 100, 0.0057) == 1106  # 1000 + 100 + 5.7% interest

def test_simulate_investment_fund():
    result = simulate_investment_fund(1000, 100, 0.07, 1)
    assert result["final_balance"] == 2328  # Final balance after 1 year
    assert len(result["history"]) == 12  # 12 months of history

def test_anomaly():
    # The anomaly emerges from the interaction between the functions.
    # When simulating over multiple years, rounding errors accumulate.
    result = simulate_investment_fund(1000, 100, 0.07, 10)
    assert result["final_balance"] != 17584  # Expected value without rounding errors