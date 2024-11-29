"""
Auto Loan Bitcoin Enhancement Analysis
====================================

This script analyzes the potential benefits of enhancing auto loans with Bitcoin purchases. 
It simulates scenarios where a borrower takes out a traditional auto loan but adds an 
additional percentage to their monthly payment to purchase Bitcoin.

Core Calculation Methodology:
---------------------------
1. Monthly Payment Calculation:
   - Uses standard amortization formula from calculate_loan_metrics() to determine base monthly payment
   - Additional Bitcoin allocation is calculated as a percentage of this base payment
   - References calculation from btc_loan_analysis.py (lines 5-17)

2. Bitcoin Purchase Simulation:
   - Purchases occur on a specified day each month (user-defined payment date)
   - Uses hourly Bitcoin price data to find the exact price at purchase time
   - Accumulates Bitcoin based on the monthly allocation divided by actual market price
   - Purchase simulation logic adapted from btc_loan_analysis.py (lines 34-56)

3. Return Calculations:
   - Total Interest Cost = Sum of all payments - Principal
   - Total BTC Investment = Monthly BTC allocation × Loan term
   - Final BTC Value = Accumulated BTC × Final BTC price
   - Net Position = Final BTC Value - Total BTC Investment
   - ROI Percentage = ((Final BTC Value - Total BTC Investment) / Total BTC Investment) × 100
   - Effective Cost = Total Interest - (Final BTC Value - Total BTC Investment)

Output Metrics Explained:
-----------------------
1. Loan Metrics:
   - Principal: Original loan amount
   - APR: Annual Percentage Rate of the loan
   - Monthly Payment: Base loan payment + Bitcoin allocation
   - Total Interest: Total interest paid over loan term
   - Total Loan Cost: Principal + Total Interest

2. Bitcoin Investment Metrics:
   - Monthly BTC Investment: Dollar amount allocated to BTC each month
   - Total BTC Investment: Sum of all BTC purchases in dollars
   - BTC Accumulated: Total Bitcoin acquired (in BTC)
   - Final BTC Value: Current market value of accumulated Bitcoin
   - Net Position: Profit/Loss on Bitcoin investment
   - ROI: Return on Investment percentage

3. Effective Cost Analysis:
   - Original Interest Cost: Interest without Bitcoin enhancement
   - Bitcoin Net Gain/Loss: Profit or loss from Bitcoin position
   - Net Interest After BTC: Effective interest cost after considering Bitcoin position
   - Effective APR/Return: Actual cost/return rate after Bitcoin enhancement

CSV Output Structure:
-------------------
The script generates 'auto_loan_analysis_results.csv' containing:
- All input parameters (principal, APR, term, BTC allocation)
- All calculated metrics for each scenario
- Time series data (start/end dates)
- Performance metrics (ROI, effective rates)

Usage:
------
Run the script and input:
1. Loan principal amount
2. APR percentage
3. Loan term (48/60/72 months)
4. Bitcoin allocation percentage
5. Preferred payment day (1-28)

The script will analyze both the user's specific scenario and generate a comprehensive 
analysis of various auto loan scenarios for comparison.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar

def generate_auto_loan_scenarios():
    """Generate base scenarios for auto loans with different parameters"""
    scenarios = []
    
    # Standard auto loan parameters
    principals = [20000, 25000, 30000, 35000, 40000, 45000, 50000]
    aprs = [3.99, 4.99, 5.99, 6.99, 7.99]
    terms = [48, 60, 72]  # 4, 5, 6 years
    btc_percentages = [5, 7.5, 10, 12.5, 15]
    
    for principal in principals:
        for apr in aprs:
            for term in terms:
                for btc_pct in btc_percentages:
                    scenarios.append({
                        'principal_amount': principal,
                        'traditional_apr': apr,
                        'loan_term_months': term,
                        'btc_purchase_percentage': btc_pct
                    })
    
    return pd.DataFrame(scenarios)

def get_user_inputs():
    """Get user inputs for custom auto loan analysis"""
    print("\nAuto Loan Bitcoin Enhancement Analysis")
    print("=====================================")
    
    principal = float(input("Enter loan principal amount ($): "))
    apr = float(input("Enter APR (%): "))
    term_months = int(input("Enter loan term (48/60/72 months): "))
    btc_percentage = float(input("Enter Bitcoin allocation percentage (%): "))
    payment_day = int(input("Enter preferred payment day (1-28): "))
    
    return {
        'principal_amount': principal,
        'traditional_apr': apr,
        'loan_term_months': term_months,
        'btc_purchase_percentage': btc_percentage,
        'payment_day': min(28, max(1, payment_day))  # Ensure day is between 1-28
    }

def analyze_auto_loan(btc_data, loan_params):
    """Analyze auto loan with Bitcoin enhancement using specified payment day"""
    # Reference core calculation logic from original script
    monthly_rate = loan_params['traditional_apr'] / 12 / 100
    monthly_payment = loan_params['principal_amount'] * (monthly_rate * (1 + monthly_rate)**loan_params['loan_term_months']) / ((1 + monthly_rate)**loan_params['loan_term_months'] - 1)
    btc_monthly_amount = monthly_payment * (loan_params['btc_purchase_percentage'] / 100)
    
    # Calculate BTC accumulation
    btc_accumulated = 0
    total_btc_investment = 0
    
    # Get the start date and generate monthly purchase dates
    start_date = btc_data['date'].max() - pd.DateOffset(months=loan_params['loan_term_months'])
    purchase_dates = pd.date_range(
        start=start_date,
        periods=int(loan_params['loan_term_months']),  # Convert to int
        freq='ME'  # Month End frequency
    )
    
    # Adjust dates to the specified payment day
    payment_dates = [
        date.replace(day=min(loan_params['payment_day'], calendar.monthrange(date.year, date.month)[1]))
        for date in purchase_dates
    ]
    
    # Filter data and simulate purchases
    period_data = btc_data[btc_data['date'] >= start_date].copy()
    
    for purchase_date in payment_dates:
        # Find closest available price to payment date/time
        day_price = period_data.loc[
            (period_data['date'] - purchase_date).abs().idxmin(),
            'avg_price'
        ]
        
        btc_purchased = btc_monthly_amount / day_price
        btc_accumulated += btc_purchased
        total_btc_investment += btc_monthly_amount
    
    # Calculate final positions and returns
    final_btc_price = period_data['avg_price'].iloc[-1]
    final_btc_value = btc_accumulated * final_btc_price
    total_interest = (monthly_payment * loan_params['loan_term_months']) - loan_params['principal_amount']
    
    return {
        'principal': loan_params['principal_amount'],
        'apr': loan_params['traditional_apr'],
        'term_months': loan_params['loan_term_months'],
        'btc_percentage': loan_params['btc_purchase_percentage'],
        'payment_day': loan_params['payment_day'],
        'monthly_payment': monthly_payment,
        'btc_monthly_amount': btc_monthly_amount,
        'total_payments': monthly_payment * loan_params['loan_term_months'],
        'total_interest': total_interest,
        'total_btc_investment': total_btc_investment,
        'btc_accumulated': btc_accumulated,
        'final_btc_value': final_btc_value,
        'net_btc_position': final_btc_value - total_btc_investment,
        'roi_percentage': ((final_btc_value - total_btc_investment) / total_btc_investment) * 100,
        'effective_cost': total_interest - (final_btc_value - total_btc_investment),
        'start_date': start_date,
        'end_date': btc_data['date'].max()
    }

def main():
    # Load BTC price data
    btc_data = pd.read_csv("Gemini_BTCUSD_1h.csv", skiprows=1)
    btc_data['date'] = pd.to_datetime(btc_data['date'], format='%m/%d/%y %H:%M')
    btc_data['avg_price'] = pd.to_numeric(btc_data['high'], errors='coerce') + pd.to_numeric(btc_data['low'], errors='coerce') / 2
    btc_data = btc_data.dropna().sort_values('date').reset_index(drop=True)
    
    # Get user inputs for custom analysis
    loan_params = get_user_inputs()
    custom_result = analyze_auto_loan(btc_data, loan_params)
    
    # Generate and analyze standard scenarios
    scenarios = generate_auto_loan_scenarios()
    all_results = []
    
    for _, scenario in scenarios.iterrows():
        scenario_params = scenario.to_dict()
        scenario_params['payment_day'] = loan_params['payment_day']  # Use same payment day
        result = analyze_auto_loan(btc_data, scenario_params)
        all_results.append(result)
    
    # Save all results to CSV
    results_df = pd.DataFrame(all_results)
    results_df.to_csv('auto_loan_analysis_results.csv', index=False)
    
    # Print custom analysis results
    print("\nCustom Auto Loan Analysis Results")
    print("================================")
    print(f"Principal: ${custom_result['principal']:,.2f}")
    print(f"APR: {custom_result['apr']}%")
    print(f"Term: {custom_result['term_months']} months")
    print(f"Payment Day: {custom_result['payment_day']}")
    print(f"\nMonthly Payment: ${custom_result['monthly_payment']:,.2f}")
    print(f"Monthly BTC Investment: ${custom_result['btc_monthly_amount']:,.2f}")
    print(f"Bitcoin Fused Auto Loan's Monthly Payment: ${custom_result['monthly_payment'] + custom_result['btc_monthly_amount']:,.2f}")
    print(f"\nTotal Interest: ${custom_result['total_interest']:,.2f}")
    print(f"Total BTC Investment: ${custom_result['total_btc_investment']:,.2f}")
    print(f"BTC Accumulated: {custom_result['btc_accumulated']:.8f} BTC")
    print(f"Final BTC Value: ${custom_result['final_btc_value']:,.2f}")
    print(f"Net BTC Position: ${custom_result['net_btc_position']:,.2f}")
    print(f"BTC ROI: {custom_result['roi_percentage']:.2f}%")
    print(f"Effective Interest Cost: ${custom_result['effective_cost']:,.2f}")

if __name__ == "__main__":
    main() 