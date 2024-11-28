def analyze_monthly_dca(df, principal_amount, monthly_btc_percentage, loan_duration_months):
    """
    Analyze the performance of monthly Bitcoin purchases alongside loan payments.
    Understand the potential returns from regular Bitcoin purchases alongside loan payments

    Args:
        df: DataFrame with historical BTC price data
        principal_amount: Total loan amount (e.g., $20,000)
        monthly_btc_percentage: Percentage of monthly payment allocated to BTC (e.g., 10%)
        loan_duration_months: Loan duration in months (e.g., 48 for 4 years)
    """
    # Calculate base monthly payment (simplified, without interest)
    base_monthly_payment = principal_amount / loan_duration_months
    monthly_btc_investment = base_monthly_payment * (monthly_btc_percentage / 100)
    
    results = []
    
    # Resample data to monthly frequency
    monthly_df = df.resample('M', on='date').agg({
        'avg_price': 'mean',
        'high': 'max',
        'low': 'min'
    })
    
    # Analyze different starting periods
    for start_idx in range(len(monthly_df) - loan_duration_months):
        period_df = monthly_df.iloc[start_idx:start_idx + loan_duration_months]
        
        # Calculate BTC accumulated
        btc_accumulated = sum(monthly_btc_investment / period_df['avg_price'])
        
        # Calculate final value
        final_btc_value = btc_accumulated * period_df['avg_price'].iloc[-1]
        total_invested = monthly_btc_investment * loan_duration_months
        roi_percentage = ((final_btc_value - total_invested) / total_invested) * 100
        
        results.append({
            'start_date': period_df.index[0],
            'end_date': period_df.index[-1],
            'btc_accumulated': btc_accumulated,
            'total_invested': total_invested,
            'final_value': final_btc_value,
            'roi_percentage': roi_percentage
        })
    
    return pd.DataFrame(results)