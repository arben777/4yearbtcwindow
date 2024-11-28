"""
Auto Loan Bitcoin Enhancement Visualization
========================================

This script creates visualizations from the auto loan analysis results CSV file.
It produces three key visualizations and a statistical summary:

1. Loan Cost Comparison (loan_cost_comparison.png):
   - Compares traditional loan costs vs. BTC-enhanced loan costs
   - Groups by APR, loan term, and BTC allocation percentage
   - Shows side-by-side bar comparison for easy cost analysis
   - Filtered by principal amount for clarity

2. ROI Heatmap (roi_heatmap.png):
   - Visualizes ROI patterns across different loan terms and BTC allocations
   - Uses color gradient to show performance variations
   - Includes actual values in each cell
   - Helps identify optimal term/allocation combinations

3. Savings Distribution (savings_distribution.png):
   - Shows potential savings distribution using box plots
   - Grouped by loan term and BTC allocation
   - Demonstrates variability in savings across different strategies
   - Helps understand risk/reward profiles

4. Strategy Performance Summary (console output):
   - Detailed statistical summary of performance metrics
   - Groups results by term length and BTC allocation
   - Shows mean ROI, savings percentages (min/max/mean)
   - Includes average effective cost

Key Metrics Calculated:
----------------------
- base_loan_cost: Principal + Total Interest
- total_cost_with_btc: Base loan cost + BTC investment - Final BTC value
- savings_percentage: Percentage saved compared to traditional loan
- ROI percentage: Return on BTC investment

Usage:
------
1. Ensure auto_loan_analysis_results.csv exists in the same directory
2. Run script: python visualize_results.py
3. Check output files and console summary

Dependencies:
------------
- pandas
- matplotlib
- seaborn
- tabulate
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tabulate import tabulate

def load_and_clean_data():
    df = pd.read_csv('auto_loan_analysis_results.csv')
    
    # Calculate total loan cost without BTC
    df['base_loan_cost'] = df['principal'] + df['total_interest']
    
    # Calculate effective total cost with BTC
    df['total_cost_with_btc'] = df['base_loan_cost'] + df['total_btc_investment'] - df['final_btc_value']
    
    # Round numerical columns
    numeric_columns = [
        'monthly_payment', 'btc_monthly_amount', 'total_payments',
        'total_interest', 'total_btc_investment', 'final_btc_value',
        'net_btc_position', 'roi_percentage', 'effective_cost',
        'base_loan_cost', 'total_cost_with_btc'
    ]
    
    for col in numeric_columns:
        df[col] = df[col].round(2)
    
    df['btc_accumulated'] = df['btc_accumulated'].round(8)
    return df

def create_cost_comparison_plot(df):
    plt.figure(figsize=(20, 10))
    
    principal = 30000
    filtered_df = df[df['principal'] == principal]
    
    # Filter for specific APRs and terms for clarity
    filtered_df = filtered_df[
        (filtered_df['apr'].isin([3.99, 4.99, 5.99, 6.99])) &
        (filtered_df['btc_percentage'].isin([5, 7.5, 10]))
    ]
    
    x = range(len(filtered_df))
    width = 0.35
    
    plt.bar(x, filtered_df['base_loan_cost'], width, label='Traditional Loan Cost')
    plt.bar([i + width for i in x], filtered_df['total_cost_with_btc'], width, 
            label='Cost with BTC Strategy')
    
    plt.title(f'Loan Cost Comparison (${principal:,} Principal)', pad=20)
    plt.xlabel('Scenarios', labelpad=15)
    plt.ylabel('Total Cost ($)', labelpad=15)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Rotate labels for better readability
    plt.xticks([i + width/2 for i in x], 
               [f'{r.apr}% APR\n{r.term_months}m/{r.btc_percentage}% BTC' 
                for _, r in filtered_df.iterrows()], 
               rotation=45)
    
    plt.tight_layout()
    plt.savefig('loan_cost_comparison.png', bbox_inches='tight')
    plt.close()

def create_roi_heatmap(df):
    plt.figure(figsize=(12, 8))
    
    # Create pivot table for heatmap
    pivot = df.pivot_table(
        values='roi_percentage',
        index='btc_percentage',
        columns='term_months',
        aggfunc='mean'
    )
    
    # Create heatmap
    sns.heatmap(pivot, annot=True, fmt='.2f', cmap='RdYlGn')
    plt.title('ROI Heatmap: BTC Allocation vs Loan Term')
    plt.xlabel('Loan Term (Months)')
    plt.ylabel('BTC Allocation (%)')
    
    plt.tight_layout()
    plt.savefig('roi_heatmap.png')
    plt.close()

def create_savings_analysis(df):
    plt.figure(figsize=(12, 6))
    
    # Calculate savings percentage
    df['savings_percentage'] = ((df['base_loan_cost'] - df['total_cost_with_btc']) / 
                              df['base_loan_cost'] * 100)
    
    sns.boxplot(x='term_months', y='savings_percentage', hue='btc_percentage', data=df)
    plt.title('Potential Savings Distribution by Term and BTC Allocation')
    plt.xlabel('Loan Term (Months)')
    plt.ylabel('Savings Percentage (%)')
    
    plt.tight_layout()
    plt.savefig('savings_distribution.png')
    plt.close()

def print_summary_stats(df):
    # Calculate savings percentage first
    df['savings_percentage'] = ((df['base_loan_cost'] - df['total_cost_with_btc']) / 
                              df['base_loan_cost'] * 100)
    
    summary = df.groupby(['term_months', 'btc_percentage']).agg({
        'roi_percentage': 'mean',
        'savings_percentage': ['mean', 'min', 'max'],
        'effective_cost': 'mean'
    }).round(2)
    
    print("\nStrategy Performance Summary")
    print("=" * 80)
    print(tabulate(summary, headers='keys', tablefmt='pretty', floatfmt=".2f"))

def create_dealership_style_comparison(df):
    """Creates a dealership-style comparison showing different terms and BTC allocations"""
    fig = plt.figure(figsize=(20, 15))
    
    # Create grid of comparisons
    terms = [48, 60, 72]  # Standard auto loan terms
    btc_pcts = [5, 7.5, 10]  # Conservative to moderate BTC allocations
    principal = 30000
    apr = 5.99
    
    grid_size = len(terms)
    
    for idx, term in enumerate(terms, 1):
        ax = plt.subplot(grid_size, 1, idx)
        
        # Get base monthly payment (same for all BTC allocations within term)
        base_scenario = df[(df['principal'] == principal) & 
                         (df['term_months'] == term) & 
                         (df['apr'] == apr) & 
                         (df['btc_percentage'] == btc_pcts[0])].iloc[0]
        base_monthly = base_scenario['monthly_payment'] - base_scenario['btc_monthly_amount']
        
        scenarios = []
        for btc_pct in btc_pcts:
            scenario = df[(df['principal'] == principal) & 
                         (df['term_months'] == term) & 
                         (df['apr'] == apr) & 
                         (df['btc_percentage'] == btc_pct)].iloc[0]
            scenarios.append(scenario)
        
        y_positions = range(len(btc_pcts))
        
        # Display comparisons
        for i, scenario in enumerate(scenarios):
            btc_monthly = base_monthly * (btc_pct/100)  # Calculate BTC allocation
            total_monthly = base_monthly + btc_monthly
            
            # Left side - Base loan details
            ax.text(0.05, i, f"${base_monthly:,.2f}/mo", va='center', fontsize=12)
            
            # Middle - BTC allocation
            ax.text(0.25, i, f"+${btc_monthly:,.2f} BTC", va='center', color='#2F4F4F', fontsize=12)
            ax.text(0.45, i, f"=${total_monthly:,.2f} total", va='center', fontsize=12)
            
            # Right side - BTC accumulation and returns
            ax.text(0.65, i, f"BTC: {scenario['btc_accumulated']:.8f}", va='center', color='#2F4F4F', fontsize=12)
            
            # Effective rate/return
            annual_rate = scenario['effective_cost']/principal*100/term*12
            if annual_rate > 0:
                rate_text = f"Effective APR: {annual_rate:.2f}%"
                color = 'red'
            else:
                rate_text = f"Annual Return: {abs(annual_rate):.2f}%"
                color = 'green'
            ax.text(0.85, i, rate_text, va='center', color=color, fontsize=12)
        
        # Section title
        ax.set_title(f'{term} Month Term @ {apr}% APR', pad=20, fontsize=14)
        ax.set_yticks(y_positions)
        ax.set_yticklabels([f'{pct}% BTC' for pct in btc_pcts], fontsize=12)
        
        # Grid and formatting
        ax.grid(True, alpha=0.2)
        ax.set_xticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    plt.suptitle(f'${principal:,} Auto Loan Comparison\nTraditional vs. Bitcoin-Enhanced Options', 
                 fontsize=16, y=0.95)
    plt.tight_layout()
    plt.savefig('dealership_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_cost_benefit_timeline(df):
    """Creates timeline visualizations for different BTC allocation percentages"""
    fig, axes = plt.subplots(1, 3, figsize=(20, 8))
    
    principal = 30000
    apr = 5.99
    term = 60
    
    # Calculate base monthly payment (same for all scenarios)
    monthly_rate = apr / 12 / 100
    base_monthly = principal * (monthly_rate * (1 + monthly_rate)**term) / ((1 + monthly_rate)**term - 1)
    
    fig.suptitle(f'Cost vs. Benefit Over Loan Term - Different BTC Allocations\n${principal:,} Principal @ {apr}% APR for {term} Months', 
                 fontsize=16, y=1.05)
    
    btc_percentages = [5, 7.5, 10]
    milestone_months = [10, 20, 30, 40, 50, 60]
    
    for idx, btc_pct in enumerate(btc_percentages):
        ax = axes[idx]
        
        # Calculate BTC allocation and total monthly for this scenario
        btc_monthly = base_monthly * (btc_pct/100)
        total_monthly = base_monthly + btc_monthly
        
        scenario = df[(df['principal'] == principal) & 
                     (df['term_months'] == term) & 
                     (df['apr'] == apr) & 
                     (df['btc_percentage'] == btc_pct)].iloc[0]
        
        months = range(int(scenario['term_months']) + 1)
        traditional_cost = [base_monthly * m for m in months]
        enhanced_cost = [total_monthly * m for m in months]
        btc_value = [scenario['final_btc_value'] * (m/int(scenario['term_months'])) for m in months]
        net_cost = [e - b for e, b in zip(enhanced_cost, btc_value)]
        bank_loan_value = [t + b for t, b in zip(traditional_cost, btc_value)]
        
        # Plot lines
        ax.plot(months, traditional_cost, label='Traditional Loan Cost', color='#FF6B6B', linewidth=2)
        ax.plot(months, enhanced_cost, label='Enhanced Loan Cost', color='#4ECDC4', linewidth=2)
        ax.plot(months, btc_value, label='Estimated BTC Value', color='#45B7D1', linestyle='--', linewidth=2)
        ax.plot(months, net_cost, label='Net Effective Cost', color='#96CEB4', linewidth=2)
        ax.plot(months, bank_loan_value, label='Bank\'s Total Loan Value', color='#FFB347', linewidth=2)
        
        # Add milestone markers and values
        for month in milestone_months:
            ax.plot(month, traditional_cost[month], 'o', color='#FF6B6B')
            ax.plot(month, enhanced_cost[month], 'o', color='#4ECDC4')
            ax.plot(month, btc_value[month], 'o', color='#45B7D1')
            ax.plot(month, net_cost[month], 'o', color='#96CEB4')
            ax.plot(month, bank_loan_value[month], 'o', color='#FFB347')
            
            if month == 30:
                ax.annotate(f'${traditional_cost[month]:,.0f}', 
                           (month, traditional_cost[month]), 
                           textcoords="offset points", 
                           xytext=(0,10), 
                           ha='center')
                ax.annotate(f'${bank_loan_value[month]:,.0f}', 
                           (month, bank_loan_value[month]), 
                           textcoords="offset points", 
                           xytext=(0,-15), 
                           ha='center')
        
        title = (f'{btc_pct}% BTC Allocation\n'
                f'Monthly: ${base_monthly:.2f} + ${btc_monthly:.2f} BTC = ${total_monthly:.2f}\n'
                f'Net borrower cost after full payout: ${net_cost[-1]:,.2f}')
        ax.set_title(title, pad=20)
        
        ax.set_xlabel('Months')
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        if idx == 0:
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    fig.text(0.04, 0.5, 'Amount ($)', va='center', rotation='vertical')
    
    plt.tight_layout()
    plt.savefig('cost_benefit_timeline.png', bbox_inches='tight', dpi=300)
    plt.close()

def main():
    df = load_and_clean_data()
    
    create_cost_comparison_plot(df)
    create_dealership_style_comparison(df)
    create_cost_benefit_timeline(df)
    print_summary_stats(df)
    
    print("\nVisualization files created:")
    print("1. loan_cost_comparison.png - Compare traditional vs BTC-enhanced loan costs")
    print("2. dealership_comparison.png - Dealership-style comparison across terms")
    print("3. cost_benefit_timeline.png - Cost vs. Benefit Over Loan Term with Net Cost")

if __name__ == "__main__":
    main()