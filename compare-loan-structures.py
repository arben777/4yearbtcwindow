def compare_loan_structures(df, loan_amount, traditional_apr, btc_percentage, loan_duration_months):
    """
    Compare traditional loans vs Bitcoin-enhanced loans over time.
    Compare the total cost/benefit analysis of traditional vs. Bitcoin-enhanced loans

    """
    traditional_monthly = calculate_monthly_payment(loan_amount, traditional_apr, loan_duration_months)
    enhanced_monthly = traditional_monthly * (1 + btc_percentage/100)
    
    results = []
    
    for start_idx in range(len(df) - (loan_duration_months * 30 * 24)):
        period_df = df.iloc[start_idx:start_idx + (loan_duration_months * 30 * 24)]
        
        # Traditional loan calculations
        traditional_total_paid = traditional_monthly * loan_duration_months
        
        # Enhanced loan calculations
        btc_monthly = traditional_monthly * (btc_percentage/100)
        btc_accumulated = simulate_btc_accumulation(period_df, btc_monthly, loan_duration_months)
        btc_final_value = btc_accumulated * period_df['avg_price'].iloc[-1]
        enhanced_total_paid = enhanced_monthly * loan_duration_months
        
        # Net position comparison
        traditional_net = -traditional_total_paid
        enhanced_net = -enhanced_total_paid + btc_final_value
        
        results.append({
            'start_date': period_df['date'].iloc[0],
            'end_date': period_df['date'].iloc[-1],
            'traditional_total_paid': traditional_total_paid,
            'enhanced_total_paid': enhanced_total_paid,
            'btc_value': btc_final_value,
            'net_difference': enhanced_net - traditional_net
        })
    
    return pd.DataFrame(results)