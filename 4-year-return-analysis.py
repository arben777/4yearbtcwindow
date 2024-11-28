import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def analyze_btc_returns(csv_path):
    """
    Analyze Bitcoin returns over 4-year intervals using Gemini hourly data.
    """
    # Skip the first row (URL) and use the second row as headers
    df = pd.read_csv(csv_path, skiprows=1, low_memory=False)
    
    # Debug: Print column names and first few rows
    print("Available columns:", df.columns.tolist())
    print("\nFirst few rows of data:")
    print(df.head())
    print("\nTotal records:", len(df))
    
    # Drop the unix column since we don't need it
    df = df.drop('unix', axis=1)
    
    # Convert date strings to datetime
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y %H:%M')
    
    # Sort by date to ensure chronological order (oldest to newest)
    df = df.sort_values('date')
    
    print(f"\nAnalyzing data from {df['date'].min()} to {df['date'].max()}")
    
    # Calculate average price for each hour
    df['avg_price'] = (df['high'].astype(float) + df['low'].astype(float)) / 2
    
    # Ensure we have valid numeric data
    df['avg_price'] = pd.to_numeric(df['avg_price'], errors='coerce')
    df = df.dropna(subset=['avg_price'])
    
    def get_exact_4_year_later_date(start_date):
        """Get the exact date 4 years later, preserving hour"""
        # Add exactly 4 years (accounting for leap years automatically)
        years_4 = pd.DateOffset(years=4)
        return start_date + years_4
    
    # Initialize lists to store returns
    all_returns = []
    all_start_dates = []
    all_end_dates = []
    
    # Slide through the dataset using datetime index
    for i in range(len(df)):
        start_date = df['date'].iloc[i]
        target_end_date = get_exact_4_year_later_date(start_date)
        
        # Find the closest matching end date in our dataset
        end_idx = df['date'].searchsorted(target_end_date)
        
        # Skip if we don't have enough data
        if end_idx >= len(df):
            break
        
        start_price = df['avg_price'].iloc[i]
        end_price = df['avg_price'].iloc[end_idx]
        
        # Calculate percentage return
        return_pct = ((end_price - start_price) / start_price) * 100
        
        all_returns.append(return_pct)
        all_start_dates.append(start_date)
        all_end_dates.append(df['date'].iloc[end_idx])
    
    # Find the highest and lowest returns
    max_return_idx = np.argmax(all_returns)
    min_return_idx = np.argmin(all_returns)
    
    # Get the corresponding end indices
    max_end_date = all_end_dates[max_return_idx]
    min_end_date = all_end_dates[min_return_idx]
    
    # Find the indices in the original dataframe
    max_end_idx = df['date'].searchsorted(max_end_date)
    min_end_idx = df['date'].searchsorted(min_end_date)
    
    results = {
        'highest_return': {
            'return_pct': all_returns[max_return_idx],
            'start_date': all_start_dates[max_return_idx],
            'end_date': all_end_dates[max_return_idx],
            'start_price': df['avg_price'].iloc[max_return_idx],
            'end_price': df['avg_price'].iloc[max_end_idx],
            'start_volume_btc': df['Volume BTC'].iloc[max_return_idx],
            'end_volume_btc': df['Volume BTC'].iloc[max_end_idx]
        },
        'lowest_return': {
            'return_pct': all_returns[min_return_idx],
            'start_date': all_start_dates[min_return_idx],
            'end_date': all_end_dates[min_return_idx],
            'start_price': df['avg_price'].iloc[min_return_idx],
            'end_price': df['avg_price'].iloc[min_end_idx],
            'start_volume_btc': df['Volume BTC'].iloc[min_return_idx],
            'end_volume_btc': df['Volume BTC'].iloc[min_end_idx]
        },
        'average_return': np.mean(all_returns),
        'median_return': np.median(all_returns),
        'return_std': np.std(all_returns),
        'total_intervals_analyzed': len(all_returns)
    }
    
    return results

def print_results(results):
    """
    Print the analysis results in a readable format.
    """
    print("\nBitcoin 4-Year Return Analysis")
    print("=" * 50)
    
    print("\nBest 4-Year Period:")
    print(f"Return: {results['highest_return']['return_pct']:.2f}%")
    print(f"Start Date: {results['highest_return']['start_date']}")
    print(f"End Date: {results['highest_return']['end_date']}")
    print(f"Start Price: ${results['highest_return']['start_price']:.2f}")
    print(f"End Price: ${results['highest_return']['end_price']:.2f}")
    print(f"Start Volume BTC: {results['highest_return']['start_volume_btc']:.2f}")
    print(f"End Volume BTC: {results['highest_return']['end_volume_btc']:.2f}")
    
    print("\nWorst 4-Year Period:")
    print(f"Return: {results['lowest_return']['return_pct']:.2f}%")
    print(f"Start Date: {results['lowest_return']['start_date']}")
    print(f"End Date: {results['lowest_return']['end_date']}")
    print(f"Start Price: ${results['lowest_return']['start_price']:.2f}")
    print(f"End Price: ${results['lowest_return']['end_price']:.2f}")
    print(f"Start Volume BTC: {results['lowest_return']['start_volume_btc']:.2f}")
    print(f"End Volume BTC: {results['lowest_return']['end_volume_btc']:.2f}")
    
    print("\nSummary Statistics:")
    print(f"Average 4-Year Return: {results['average_return']:.2f}%")
    print(f"Median 4-Year Return: {results['median_return']:.2f}%")
    print(f"Standard Deviation: {results['return_std']:.2f}%")
    print(f"Total Intervals Analyzed: {results['total_intervals_analyzed']}")

# Usage
if __name__ == "__main__":
    csv_path = "/Users/arben/Downloads/Gemini_BTCUSD_1h.csv"  # Replace with your CSV file path
    try:
        results = analyze_btc_returns(csv_path)
        print_results(results)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
