"""
This will create a loan_scenarios.csv file with realistic loan parameters. 
For the monthly payment simulation data, we should create another CSV: monthly_payment_simulation.csv
"""

import pandas as pd
import numpy as np

def generate_loan_scenarios():
    scenarios = {
        'loan_type': [
            'Auto Loan', 'Auto Loan', 'Auto Loan',
            'Mortgage', 'Mortgage', 'Mortgage',
            'Personal Loan', 'Personal Loan', 'Personal Loan'
        ],
        'principal_amount': [
            20000, 35000, 50000,
            300000, 500000, 750000,
            10000, 25000, 40000
        ],
        'traditional_apr': [
            5.99, 6.99, 7.99,
            4.99, 5.49, 5.99,
            8.99, 9.99, 11.99
        ],
        'loan_term_months': [
            36, 48, 60,
            360, 360, 360,
            24, 36, 48
        ],
        'btc_purchase_percentage': [
            5, 7.5, 10,
            2.5, 5, 7.5,
            5, 7.5, 10
        ]
    }
    
    df = pd.DataFrame(scenarios)
    df.to_csv('loan_scenarios.csv', index=False)
    return df

def generate_monthly_payment_scenarios():
    # Create date range for the last 8 years (to match with BTC data)
    dates = pd.date_range(start='2015-01-01', end='2023-12-31', freq='ME')
    
    scenarios = []
    
    # Generate different payment scenarios
    for loan_amount in [20000, 35000, 50000]:  # Sample loan amounts
        for btc_percentage in [5, 7.5, 10]:  # Sample BTC allocation percentages
            monthly_payment = loan_amount / 48  # Simplified 4-year term
            btc_allocation = monthly_payment * (btc_percentage / 100)
            
            for date in dates:
                scenarios.append({
                    'date': date,
                    'loan_amount': loan_amount,
                    'btc_percentage': btc_percentage,
                    'monthly_payment': monthly_payment,
                    'btc_allocation': btc_allocation
                })
    
    df = pd.DataFrame(scenarios)
    df.to_csv('monthly_payment_scenarios.csv', index=False)
    return df

if __name__ == "__main__":
    scenarios_df = generate_loan_scenarios()
    print("Generated loan scenarios:")
    print(scenarios_df)
    
    # Generate the payment scenarios
    payment_scenarios_df = generate_monthly_payment_scenarios()
    print(payment_scenarios_df.head()) 