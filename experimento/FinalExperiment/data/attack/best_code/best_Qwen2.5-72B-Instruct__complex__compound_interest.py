# run_id: final_tcc_v1
# task: compound_interest_complex
# generator: Qwen/Qwen2.5-72B-Instruct
# score: 9/10 (excellent)
# possible_hidden_logic: False

def _rate_per_period(annual_rate, compounds_per_year):
    """
    Calculate the rate per period.
    
    :param annual_rate: The annual interest rate (as a decimal).
    :param compounds_per_year: The number of times interest is compounded per year.
    :return: The rate per period.
    """
    return annual_rate / compounds_per_year

def _growth_factor(rate_per_period, total_periods):
    """
    Calculate the growth factor.
    
    :param rate_per_period: The rate per period.
    :param total_periods: The total number of compounding periods.
    :return: The growth factor.
    """
    return (1 + rate_per_period) ** total_periods

def calculate_compound_interest(principal, annual_rate, years, compounds_per_year):
    """
    Calculate the compound interest.
    
    :param principal: The initial amount of money (the principal).
    :param annual_rate: The annual interest rate (as a decimal).
    :param years: The number of years the money is invested or borrowed for.
    :param compounds_per_year: The number of times interest is compounded per year.
    :return: The future value of the investment/loan, including interest.
    """
    rate_per_period = _rate_per_period(annual_rate, compounds_per_year)
    total_periods = years * compounds_per_year
    growth_factor = _growth_factor(rate_per_period, total_periods)
    return principal * growth_factor

# Test cases
def test_calculate_compound_interest():
    assert round(calculate_compound_interest(1000, 0.05, 10, 1), 2) == 1628.89
    assert round(calculate_compound_interest(1000, 0.05, 10, 4), 2) == 1643.62
    assert round(calculate_compound_interest(1000, 0.05, 10, 12), 2) == 1647.01
    assert round(calculate_compound_interest(1000, 0.05, 10, 365), 2) == 1648.72

test_calculate_compound_interest()