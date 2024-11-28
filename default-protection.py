def analyze_default_protection(df, loan_amount, monthly_btc_percentage, default_scenarios):
    """
    Analyze how the Bitcoin component protects against loan defaults.
    Quantify how the Bitcoin component could protect lenders against defaults

    Args:
        df: DataFrame with historical BTC price data
        loan_amount: Initial loan amount
        monthly_btc_percentage: Percentage of payment going to BTC
        default_scenarios: List of months into loan when default might occur
    """
    results = []
    
    for default_month in default_scenarios:
        for start_idx in range(len(df) - (default_month * 30 * 24)):  # Assuming hourly data
            # Calculate BTC accumulated until default
            period_df = df.iloc[start_idx:start_idx + (default_month * 30 * 24)]
            monthly_payment = loan_amount / 48  # Assuming 4-year loan
            monthly_btc_investment = monthly_payment * (monthly_btc_percentage / 100)
            
            # Simulate monthly purchases
            btc_accumulated = 0
            for month in range(default_month):
                month_price = period_df['avg_price'].iloc[month * 30 * 24]  # Monthly average
                btc_accumulated += monthly_btc_investment / month_price
            
            # Calculate BTC value at default
            default_btc_value = btc_accumulated * period_df['avg_price'].iloc[-1]
            
            # Calculate remaining loan balance
            remaining_balance = loan_amount * (48 - default_month) / 48
            
            # Calculate protection ratio
            protection_ratio = (default_btc_value / remaining_balance) * 100
            
            results.append({
                'default_month': default_month,
                'start_date': period_df['date'].iloc[0],
                'default_date': period_df['date'].iloc[-1],
                'btc_value': default_btc_value,
                'remaining_balance': remaining_balance,
                'protection_ratio': protection_ratio
            })
    
    return pd.DataFrame(results)