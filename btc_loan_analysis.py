import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_loan_metrics(principal, apr, term_months, btc_percentage):
    """
    Calculate loan payments and Bitcoin purchase amounts
    """
    monthly_rate = apr / 12 / 100
    monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**term_months) / ((1 + monthly_rate)**term_months - 1)
    btc_monthly_amount = monthly_payment * (btc_percentage / 100)
    
    return {
        'monthly_payment': monthly_payment,
        'btc_monthly_amount': btc_monthly_amount,
        'total_payments': monthly_payment * term_months
    }

def analyze_btc_enhanced_loan(btc_data, loan_scenario):
    """
    Analyze a loan scenario with Bitcoin enhancement
    """
    loan_metrics = calculate_loan_metrics(
        loan_scenario['principal_amount'],
        loan_scenario['traditional_apr'],
        loan_scenario['loan_term_months'],
        loan_scenario['btc_purchase_percentage']
    )
    
    # Calculate BTC accumulation
    btc_accumulated = 0
    total_btc_investment = 0
    
    # Get the start date and generate monthly purchase dates
    start_date = btc_data['date'].max() - pd.DateOffset(months=loan_scenario['loan_term_months'])
    purchase_dates = pd.date_range(
        start=start_date,
        periods=loan_scenario['loan_term_months'],
        freq='ME'  # Monthly frequency
    )
    
    # Filter data to relevant period
    period_data = btc_data[btc_data['date'] >= start_date].copy()
    
    # Simulate monthly purchases on specific dates
    for purchase_date in purchase_dates:
        # Find the closest trading day's price
        day_price = period_data.loc[
            (period_data['date'] - purchase_date).abs().idxmin(),
            'avg_price'
        ]
        
        # Calculate BTC purchased this month
        btc_purchased = loan_metrics['btc_monthly_amount'] / day_price
        btc_accumulated += btc_purchased
        total_btc_investment += loan_metrics['btc_monthly_amount']
    
    # Get final BTC value using the end date price
    final_btc_price = period_data['avg_price'].iloc[-1]
    final_btc_value = btc_accumulated * final_btc_price
    
    # Calculate ROI percentage
    roi_percentage = ((final_btc_value - total_btc_investment) / total_btc_investment) * 100 if total_btc_investment > 0 else 0
    
    # Calculate effective rates
    effective_apr, effective_apy, rate_type = calculate_effective_rates(
        loan_metrics['total_payments'] - loan_scenario['principal_amount'],
        final_btc_value - total_btc_investment,
        loan_scenario['principal_amount'],
        loan_scenario['loan_term_months']
    )
    
    return {
        'loan_type': loan_scenario['loan_type'],
        'principal': loan_scenario['principal_amount'],
        'apr': loan_scenario['traditional_apr'],
        'total_loan_cost': loan_metrics['total_payments'],
        'monthly_payment': loan_metrics['monthly_payment'],
        'btc_monthly_amount': loan_metrics['btc_monthly_amount'],
        'total_btc_investment': total_btc_investment,
        'btc_accumulated': btc_accumulated,
        'final_btc_value': final_btc_value,
        'net_position': final_btc_value - total_btc_investment,
        'roi_percentage': roi_percentage,
        'start_date': start_date,
        'end_date': btc_data['date'].max(),
        'interest_cost': loan_metrics['total_payments'] - loan_scenario['principal_amount'],
        'net_interest_after_btc': (loan_metrics['total_payments'] - loan_scenario['principal_amount']) - (final_btc_value - total_btc_investment),
        'effective_apr': effective_apr,
        'effective_apy': effective_apy,
        'rate_type': rate_type
    }

def calculate_effective_rates(total_interest, net_bitcoin_position, principal, term_months):
    """
    Calculate effective rates or investment returns after considering Bitcoin gains
    """
    # Net interest cost after Bitcoin gains
    net_interest = total_interest - net_bitcoin_position
    
    if net_interest > 0:
        # Still paying net interest - calculate effective APR/APY
        effective_annual_rate = ((net_interest + principal) / principal) ** (12/term_months) - 1
        effective_apr = effective_annual_rate * 100
        effective_apy = (1 + effective_annual_rate/12)**12 - 1
        effective_apy *= 100
        return effective_apr, effective_apy, "cost"
    else:
        # Bitcoin gains exceeded interest - calculate returns
        total_gain = abs(net_interest)  # The amount made after covering interest
        total_capital_deployed = principal + total_interest + net_bitcoin_position  # Include Bitcoin investment
        
        # Calculate return on total capital deployed
        annual_return = (1 + total_gain/total_capital_deployed) ** (12/term_months) - 1
        annualized_return = annual_return * 100
        
        # Calculate total return percentage on all money paid
        total_return = (total_gain/total_capital_deployed) * 100
        
        return annualized_return, total_return, "return"

def main():
    # Load data
    btc_data = pd.read_csv("Gemini_BTCUSD_1h.csv", skiprows=1)
    loan_scenarios = pd.read_csv("loan_scenarios.csv")
    
    # Process BTC data with proper numeric conversion
    btc_data['date'] = pd.to_datetime(btc_data['date'], format='%m/%d/%y %H:%M')
    btc_data['high'] = pd.to_numeric(btc_data['high'], errors='coerce')
    btc_data['low'] = pd.to_numeric(btc_data['low'], errors='coerce')
    btc_data['avg_price'] = (btc_data['high'] + btc_data['low']) / 2
    
    # Drop any rows with NaN values
    btc_data = btc_data.dropna(subset=['avg_price'])
    
    # Sort and reset index
    btc_data = btc_data.sort_values('date').reset_index(drop=True)
    
    # Analyze each loan scenario
    results = []
    for _, scenario in loan_scenarios.iterrows():
        result = analyze_btc_enhanced_loan(btc_data, scenario)
        results.append(result)
    
    # Convert results to DataFrame and save
    results_df = pd.DataFrame(results)
    results_df.to_csv('btc_loan_analysis_results.csv', index=False)
    
    # Print summary
    print("\nBitcoin-Enhanced Loan Analysis")
    print("=" * 50)
    for _, result in results_df.iterrows():
        print(f"\nLoan Type: {result['loan_type']}")
        print(f"Loan Period: {result['start_date'].strftime('%Y-%m-%d')} to {result['end_date'].strftime('%Y-%m-%d')}")
        
        print("\nLoan Details:")
        print(f"Principal: ${result['principal']:,.2f}")
        print(f"Original APR: {result['apr']:.2f}%")
        print(f"Monthly Payment: ${result['monthly_payment']:,.2f}")
        print(f"Interest Cost: ${result['interest_cost']:,.2f}")
        print(f"Total Loan Cost: ${result['total_loan_cost']:,.2f}")
        
        print("\nBitcoin Investment Details:")
        print(f"Monthly BTC Investment: ${result['btc_monthly_amount']:,.2f}")
        print(f"Total BTC Investment: ${result['total_btc_investment']:,.2f}")
        print(f"BTC Accumulated: {result['btc_accumulated']:.8f} BTC")
        print(f"Final BTC Value: ${result['final_btc_value']:,.2f}")
        print(f"Net Position: ${result['net_position']:,.2f}")
        print(f"ROI: {result['roi_percentage']:.2f}%")
        
        print("\nEffective Cost Analysis:")
        print(f"Original Interest Cost: ${result['interest_cost']:,.2f}")
        print(f"Bitcoin Net Gain/Loss: ${result['net_position']:,.2f}")
        print(f"Net Interest After BTC: ${result['net_interest_after_btc']:,.2f}")
        if result['net_interest_after_btc'] > 0:
            print(f"Effective APR: {result['effective_apr']:.2f}%")
            print(f"Effective APY: {result['effective_apy']:.2f}%")
        else:
            print(f"Annualized Return: {abs(result['effective_apr']):.2f}%")
            print(f"Total Return: {abs(result['effective_apy']):.2f}%")
        print(f"Rate Type: {result['rate_type']}")
        print("-" * 50)

if __name__ == "__main__":
    main() 