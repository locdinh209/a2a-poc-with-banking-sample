# common/mock_data.py
CUSTOMERS = {
    "CUST-001": {
        "name": "Alice Smith",
        "dob": "1985-04-12",
        "id_number": "ID-123456789",
        "credit_score": 750,
        "monthly_income": 8500,
        "existing_debt": 2000,
        "is_sanctioned": False
    },
    "CUST-002": {
        "name": "Bob Jones",
        "dob": "1992-11-23",
        "id_number": "ID-987654321",
        "credit_score": 580,
        "monthly_income": 4000,
        "existing_debt": 3000,
        "is_sanctioned": False
    },
    "CUST-003": {
        "name": "Charlie Danger",
        "dob": "1978-08-30",
        "id_number": "ID-555555555",
        "credit_score": 620,
        "monthly_income": 5000,
        "existing_debt": 1000,
        "is_sanctioned": True
    }
}

TRANSACTIONS = {
    "CUST-001": [
        {"date": "2023-10-01", "amount": 1500, "category": "Rent", "type": "debit"},
        {"date": "2023-10-05", "amount": 200, "category": "Groceries", "type": "debit"},
        {"date": "2023-10-15", "amount": 4250, "category": "Salary", "type": "credit"},
        {"date": "2023-10-20", "amount": 300, "category": "Utilities", "type": "debit"},
        {"date": "2023-10-25", "amount": 500, "category": "Savings", "type": "debit"}
    ],
    "CUST-002": [
        {"date": "2023-10-01", "amount": 1800, "category": "Rent", "type": "debit"},
        {"date": "2023-10-10", "amount": 400, "category": "Entertainment", "type": "debit"},
        {"date": "2023-10-15", "amount": 2000, "category": "Salary", "type": "credit"},
        {"date": "2023-10-28", "amount": 300, "category": "Credit Card Payment", "type": "debit"}
    ],
    "CUST-003": [
        {"date": "2023-10-05", "amount": 10000, "category": "Transfer In", "type": "credit"},
        {"date": "2023-10-06", "amount": 9500, "category": "Cryptocurrency", "type": "debit"}
    ]
}
