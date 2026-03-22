from langchain_core.tools import tool
from common.mock_data import CUSTOMERS

@tool
def get_customer_data(customer_id: str) -> str:
    """Retrieve basic customer data including credit score and income.
    
    Args:
        customer_id (str): The unique identifier for the customer (e.g. CUST-001).
    """
    if customer_id not in CUSTOMERS:
        return f"Error: Customer {customer_id} not found."
    
    data = CUSTOMERS[customer_id]
    return (
        f"Customer Data:\n"
        f"- Name: {data['name']}\n"
        f"- Credit Score: {data['credit_score']}\n"
        f"- Monthly Income: ${data['monthly_income']}\n"
        f"- Existing Debt: ${data['existing_debt']}\n"
        f"- Debt-to-Income (DTI) Ratio: {(data['existing_debt'] / data['monthly_income']) * 100:.1f}%"
    )

@tool
def evaluate_loan_eligibility(credit_score: int, dti_ratio: float, requested_amount: float) -> str:
    """Evaluate if a loan should be approved based on credit score, debt-to-income, and requested amount.
    
    Args:
        credit_score (int): The customer's credit score.
        dti_ratio (float): The customer's debt-to-income ratio (as a percentage).
        requested_amount (float): The amount of the loan requested.
    """
    if credit_score < 600:
        return "Rejected: Credit score too low (minimum is 600)."
    
    if dti_ratio > 40.0:
        return "Rejected: Debt-to-Income ratio too high (maximum is 40%)."
        
    if requested_amount > 50000 and credit_score < 700:
        return "Rejected: Credit score below 700 requires amount to be <= 50,000."
        
    return "Approved: Customer meets all criteria for the requested loan."
