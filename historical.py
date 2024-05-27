import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame
from datetime import datetime

def download_data(ticker: str, start: str, end: str) -> DataFrame:
    """Download historical daily data for a given ticker symbol."""
    data = yf.download(ticker, start=start, end=end)[['Close']]
    return data

def compute_daily_returns(data: DataFrame) -> DataFrame:
    """Compute daily returns based on historical closing prices."""
    pd.options.mode.copy_on_write = True
    data['Return'] = data['Close'].pct_change()
    data = data.dropna()
    return data

def compute_leveraged_returns(data: DataFrame, leverage: float, initial_value: float) -> DataFrame:
    """Create a leveraged version of the daily returns."""
    data['Leveraged Return'] = data['Return'] * leverage
    data['Leveraged Close'] = (1 + data['Leveraged Return']).cumprod() * initial_value
    return data

def adjust_for_mer(data: DataFrame, mer: float, initial_value: float) -> DataFrame:
    """Adjust daily returns for the Management Expense Ratio (MER)."""
    daily_mer = mer / 252
    data['Adjusted Return'] = data['Leveraged Return'] - daily_mer
    data['Adjusted Close'] = (1 + data['Adjusted Return']).cumprod() * initial_value
    return data

def plot_daily_returns(data: DataFrame, title: str, leverage: float, time_unit='Year') -> None:
    """Plot the daily returns of the given data."""
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data['Close'], label='Base Index', color='blue', linewidth=0.5)
    plt.plot(data.index, data['Leveraged Close'], label=f'{leverage}x Leverage', color='red', linewidth=0.5)
    plt.plot(data.index, data['Adjusted Close'], label=f'MER Adjusted {leverage}x Leverage', color='green', linewidth=0.5)
    plt.title(f'{title}')
    plt.xlabel(time_unit)
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()

def main() -> None:
    """Main function to download data, compute daily returns, 
    create leveraged returns, and plot them for multiple indices."""
    
    indices = {
        "S&P 500": "^GSPC",
        "NASDAQ Composite": "^IXIC",
        "Dow Jones Industrial Average": "^DJI",
        "TSX Composite": "^GSPTSE"
    }
    
    start_date = "1900-01-01"
    end_date = datetime.today().strftime("%Y-%m-%d")

    leverage_factor = 2.0
    mer = 0.01

    for name, ticker in indices.items():
        # Step 1: Download historical data
        data = download_data(ticker, start_date, end_date)
        if data.empty:
            continue
        initial_value = data['Close'].iloc[0]
        
        # Step 2: Compute daily returns
        data = compute_daily_returns(data)
        
        # Step 3: Create leveraged returns
        data = compute_leveraged_returns(data, leverage_factor, initial_value)
        
        # Step 4: Adjust the leveraged returns for the MER
        data = adjust_for_mer(data, mer, initial_value)
        
        # Display the data with daily returns
        print(f"Data for {name}:")
        print(data)
        
        # Optionally, save the data to a CSV file
        data.to_csv(f'{name.lower().replace(" ", "_")}_data.csv')
        
        # Step 5: Plot the daily returns
        plot_daily_returns(data, name, leverage_factor)

if __name__ == "__main__":
    main()
