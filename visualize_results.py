import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_loan_comparisons(results_file):
    df = pd.read_csv(results_file)
    
    # Create ROI comparison plot
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x='loan_type', y='roi_percentage')
    plt.title('ROI Comparison by Loan Type')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('roi_comparison.png')
    
    # Create investment vs return plot
    plt.figure(figsize=(12, 6))
    x = df['total_btc_investment']
    y = df['final_btc_value']
    plt.scatter(x, y)
    plt.plot([min(x), max(x)], [min(x), max(x)], 'r--')  # Break-even line
    plt.xlabel('Total BTC Investment ($)')
    plt.ylabel('Final BTC Value ($)')
    plt.title('Investment vs Return')
    plt.tight_layout()
    plt.savefig('investment_return.png')

if __name__ == "__main__":
    plot_loan_comparisons('btc_loan_analysis_results.csv') 