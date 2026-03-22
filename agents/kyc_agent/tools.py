from langchain_core.tools import tool
from common.mock_data import CUSTOMERS

@tool
def verify_identity(customer_id: str, provided_name: str, provided_dob: str) -> str:
    """Verify a customer's identity by comparing provided name and DOB with internal records.
    
    Args:
        customer_id (str): The unique customer identifier.
        provided_name (str): The name provided by the customer for verification.
        provided_dob (str): The date of birth provided by the customer (YYYY-MM-DD).
    """
    if customer_id not in CUSTOMERS:
        return f"Verification Failed: Customer ID {customer_id} does not exist in our systems."
        
    record = CUSTOMERS[customer_id]
    
    if record["name"].lower() != provided_name.lower():
        return f"Verification Failed: Name mismatch. Expected {record['name']}, got {provided_name}."
        
    if record["dob"] != provided_dob:
        return f"Verification Failed: DOB mismatch."
        
    return "Identity Verified Successfully."

@tool
def check_sanctions_list(customer_id: str) -> str:
    """Check if the given customer is on any international sanctions or watchlists.
    
    Args:
        customer_id (str): The customer identifier to check.
    """
    if customer_id not in CUSTOMERS:
        return f"Error: Customer {customer_id} not found."
        
    record = CUSTOMERS[customer_id]
    
    if record["is_sanctioned"]:
        return "ALERT: Customer is present on an active sanctions list. All services must be denied."
        
    return "Clear: Customer is not on any known sanctions lists."
