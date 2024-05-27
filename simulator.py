import pandas as pd
import numpy as np
import historical as hist
from datetime import datetime
from pandas import DataFrame

def generate_random_returns(reference_data: DataFrame, size: int, initial_value: float, mer: float, leverage: float) -> DataFrame:
    """Generates a dataframe with random daily returns"""
    data = pd.DataFrame({
        'Return': np.random.choice(reference_data['Return'], size=size, replace=True)
    })
    data['Close'] = (1 + data['Return']).cumprod() * initial_value
    data = hist.compute_leveraged_returns(data, leverage, initial_value)
    data = hist.adjust_for_mer(data, mer, initial_value)
    
    return data

def main() -> None:
    """Main function to download data, simulate daily returns, 
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
    initial_value = 1.0
    time_period = 50000      # equivalent to about {this over 250} years

    for name, ticker in indices.items():
        # Step 1: Download historical data
        reference_data = hist.compute_daily_returns(hist.download_data(ticker, start_date, end_date))
        if reference_data.empty:
            continue
        
        simulated_data = generate_random_returns(reference_data, time_period, initial_value, mer, leverage_factor)
        
        print(f"Data for {name}:")
        print(reference_data)
        print(simulated_data)
        
        hist.plot_daily_returns(simulated_data, name, leverage_factor, 'Day')

if __name__ == "__main__":
    main()
