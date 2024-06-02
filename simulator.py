import numpy as np
import matplotlib.pyplot as plt
import os
import historical as hist
from datetime import datetime
from pandas import DataFrame

"""Generates a dataframe with random daily returns"""
def generate_random_returns(reference_data: DataFrame, *, size=7500, initial_value=1.0, mer=0.01, leverage=2.0) -> DataFrame:
    data = reference_data.copy()
    data = hist.compute_daily_returns(data)
    data = DataFrame({
        hist.Columns.RETURN: np.random.choice(data[hist.Columns.RETURN], size=size, replace=True)
        })
    data[hist.Columns.CLOSE] = (1 + data[hist.Columns.RETURN]).cumprod() * initial_value
    data = hist.compute_leveraged_returns(data, leverage=leverage, initial_value=initial_value)
    data = hist.adjust_for_mer(data, mer=mer, initial_value=initial_value)
    return data


"""Main function to download data, simulate daily returns, 
create leveraged returns, and plot them for multiple indices."""
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
    initial_value = 1.0
    time_period = 252 * 30    # there are 252 business days in a year

    for name, ticker in indices.items():
        # Step 1: Download historical data
        reference_data = hist.compute_daily_returns(hist.download_data(ticker, start=start_date, end=end_date))
        if reference_data.empty:
            continue
        
        # Step 2: Simulate index performance over the specified length of time
        simulated_data = generate_random_returns(reference_data, size=time_period, initial_value=initial_value, mer=mer, leverage=leverage_factor)
        
        print(f"Data for {name}:")
        print(reference_data)
        print(simulated_data)
        
        # Step 3: Plot the results
        title = f'{name} Simulation {round(len(simulated_data) / 252)} Years'
        hist.plot_data(simulated_data, title=title, leverage=leverage_factor, time_unit='Day')

if __name__ == "__main__":
    main()
