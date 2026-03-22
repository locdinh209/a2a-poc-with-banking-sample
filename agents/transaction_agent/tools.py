from langchain_core.tools import tool
from common.mock_data import TRANSACTIONS

@tool
def get_recent_transactions(customer_id: str, limit: int = 10) -> str:
    """Retrieve a list of recent transactions for a customer.
    
    Args:
        customer_id (str): The customer identifier to retrieve transactions for.
        limit (int): The maximum number of recent transactions to retrieve.
    """
    if customer_id not in TRANSACTIONS:
        return f"Error: No transactions found for customer {customer_id}."
        
    txs = TRANSACTIONS[customer_id]
    recent_txs = txs[-limit:]
    
    if not recent_txs:
        return "No recent transactions found."
        
    lines = [f"Found {len(recent_txs)} recent transactions:"]
    for tx in recent_txs:
        sign = "+" if tx["type"] == "credit" else "-"
        lines.append(f"  [{tx['date']}] {tx['category']}: {sign}${tx['amount']}")
        
    return "\n".join(lines)

@tool
def summarize_spending_patterns(customer_id: str) -> str:
    """Summarize spending patterns and categorize expenses for a customer.
    
    Args:
        customer_id (str): The customer identifier to analyze.
    """
    if customer_id not in TRANSACTIONS:
        return f"Error: No transactions found for customer {customer_id} to summarize."
        
    txs = TRANSACTIONS[customer_id]
    
    total_income = 0
    total_expenses = 0
    categories = {}
    
    for tx in txs:
        if tx["type"] == "credit":
            total_income += tx["amount"]
        elif tx["type"] == "debit":
            total_expenses += tx["amount"]
            cat = tx["category"]
            categories[cat] = categories.get(cat, 0) + tx["amount"]
            
    summary = (
        f"Spending Summary for {customer_id}:\n"
        f"- Total Income: ${total_income}\n"
        f"- Total Expenses: ${total_expenses}\n"
        f"- Net Cashflow: ${total_income - total_expenses}\n"
        f"\nTop Expense Categories:\n"
    )
    
    for cat, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        summary += f"  - {cat}: ${amount}\n"
        
    return summary
