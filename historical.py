import yfinance as yf
import matplotlib.pyplot as plt
import os
from pandas import DataFrame
from datetime import datetime
from enum import StrEnum

class Columns(StrEnum):
    CLOSE = 'Close'
    RETURN = 'Return'
    LEV_CLOSE = 'Leveraged Close'
    LEV_RETURN = 'Leveraged Return'
    ADJ_CLOSE = 'Adjusted Close'
    ADJ_RETURN = 'Adjusted Return'

"""Download historical daily data for a given ticker symbol."""
def download_data(ticker: str, *, start='1900-01-01', end=datetime.today().strftime("%Y-%m-%d")) -> DataFrame:
    return yf.download(ticker, start=start, end=end)[[Columns.CLOSE]]

"""Compute daily returns based on historical closing prices."""
def compute_daily_returns(data: DataFrame) -> DataFrame:
    new_data = data.copy()
    new_data[Columns.RETURN] = new_data[Columns.CLOSE].pct_change()
    new_data = new_data.dropna()
    return new_data

"""Compute the leveraged version of the daily returns."""
def compute_leveraged_returns(data: DataFrame, *, leverage: float, initial_value=1.0, prefix=False) -> DataFrame:
    lev_close = column_prefixer(Columns.LEV_CLOSE, leverage) if prefix else Columns.LEV_CLOSE
    lev_return = column_prefixer(Columns.LEV_RETURN, leverage) if prefix else Columns.LEV_RETURN
    
    new_data = data.copy()
    new_data[lev_return] = new_data[Columns.RETURN] * leverage
    new_data[lev_close] = (1 + new_data[lev_return]).cumprod() * initial_value
    return new_data

"""Adjust leveraged returns for the Management Expense Ratio (MER)."""
def adjust_for_mer(data: DataFrame, *, mer: float, initial_value=1.0, prefix='') -> DataFrame:
    adj_close = column_prefixer(Columns.ADJ_CLOSE, prefix) if prefix else Columns.ADJ_CLOSE
    adj_return = column_prefixer(Columns.ADJ_RETURN, prefix) if prefix else Columns.ADJ_RETURN
    lev_return = column_prefixer(Columns.LEV_RETURN, prefix) if prefix else Columns.LEV_RETURN
    daily_mer = mer / 252
    
    new_data = data.copy()
    column = lev_return if lev_return in new_data.columns else Columns.RETURN
    new_data[adj_return] = new_data[column] - daily_mer
    new_data[adj_close] = (1 + new_data[adj_return]).cumprod() * initial_value
    return new_data

"""Compute the MER adjusted leveraged version of the daily returns for multiple leverages."""
def compute_multiple_leverages(data: DataFrame, *, leverages: list[float], mers: list[float], initial_value=1.0) -> DataFrame:
    # Ensure data has a Return column
    new_data = data.copy()
    if Columns.RETURN not in new_data.columns:
        new_data = compute_daily_returns(new_data)
    
    # Remove any pre-existing leverage columns
    for col in Columns:
        if col != Columns.CLOSE and col != Columns.RETURN and col in new_data.columns:
            del new_data[col]
    
    # Add specifically labeled leverage columns
    for leverage, mer in zip(leverages, mers):
        new_data = compute_leveraged_returns(new_data, leverage=leverage, initial_value=initial_value, prefix=True)
        new_data = adjust_for_mer(new_data, mer=mer, initial_value=initial_value, prefix=str(leverage))
    return new_data

"""Plot the base, leveraged, and MER adjusted returns of the given data."""
def plot_data(data: DataFrame, *, title: str, leverage=2.0, time_unit='Year', y_axis='Price') -> None:
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data[Columns.CLOSE], label='Base Index', color='blue', linewidth=0.5)
    if not data[Columns.LEV_CLOSE].empty:
        plt.plot(data.index, data[Columns.LEV_CLOSE], label=f'{leverage}x Leverage', color='red', linewidth=0.5)
    if not data[Columns.ADJ_CLOSE].empty:
        plt.plot(data.index, data[Columns.ADJ_CLOSE], label=f'MER Adjusted {leverage}x Leverage', color='green', linewidth=0.5)
    finish_plot(title, time_unit, y_axis)

"""Plot base vs multiple leverages of the given data."""
def plot_multiple_leverage(data: DataFrame, *, title: str, leverages: list[float], time_unit='Year', y_axis='Price') -> None:
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data[Columns.CLOSE], label='Base Index', color='blue', linewidth=0.5)
    for leverage in leverages:
        column = f'{leverage}x {Columns.ADJ_CLOSE}'
        if not data[column].empty:
            plt.plot(data.index, data[column], label=f'{leverage}x Leverage', linewidth=0.5)
    finish_plot(title, time_unit, y_axis)
    
def finish_plot(title: str, x_axis: str, y_axis: str) -> None:
    if y_axis == 'Return':
        plt.axhline(color='black')
    plt.title(title)
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join('static', 'images', f'{title.lower().replace(" ", "_")}.png'))
    plt.show()
    plt.close()
    
def column_prefixer(col: Columns, leverage: float|str) -> str:
    return f'{leverage}x {col}'


"""
Main function to download data, compute daily returns, 
create leveraged returns, and plot them for multiple indices.
"""
def main() -> None:
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
        data = download_data(ticker, start=start_date, end=end_date)
        if data.empty:
            continue
        initial_value = data[Columns.CLOSE].iloc[0]
        
        # Step 2: Compute daily returns
        data = compute_daily_returns(data)
        
        # Step 3: Create leveraged returns
        data = compute_leveraged_returns(data, leverage=leverage_factor, initial_value=initial_value)
        
        # Step 4: Adjust the leveraged returns for the MER
        data = adjust_for_mer(data, mer=mer, initial_value=initial_value)
        
        # Step 5: Plot the daily returns
        plot_data(data, leverage=leverage_factor, title=f'{name} Price History')
        
        # Step 6: Compare multiple leverages (MER adjusted)
        levs = [2.0, 3.0]
        mers = [0.01, 0.01]
        data = compute_multiple_leverages(data, leverages=levs, mers=mers, initial_value=initial_value)
        plot_multiple_leverage(data, leverages=levs, title=f'{name} Price History')
        
        # Display the data with daily returns
        print(f"Data for {name}:")
        print(data)
        
        # Optionally, save the data to a CSV file
        data.to_csv(os.path.join('static', 'csvs', f'{name.lower().replace(" ", "_")}_data.csv'))
        

if __name__ == "__main__":
    main()
