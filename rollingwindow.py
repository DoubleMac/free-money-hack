import historical as hist
from datetime import datetime
from pandas import DataFrame

"""Generates a dataframe with rolling returns."""
def generate_rolling_returns(reference_data: DataFrame, *, window=2520, initial_value=1.0, mer=0.01, leverage=2.0) -> DataFrame:
    data = reference_data.copy()
    data = hist.compute_daily_returns(data)
    data = hist.compute_leveraged_returns(data, leverage=leverage, initial_value=initial_value)
    data = hist.adjust_for_mer(data, mer=mer, initial_value=initial_value)
    
    data[hist.Columns.CLOSE] = data[hist.Columns.CLOSE].pct_change(window) * 100
    data[hist.Columns.LEV_CLOSE] = data[hist.Columns.LEV_CLOSE].pct_change(window) * 100
    data[hist.Columns.ADJ_CLOSE] = data[hist.Columns.ADJ_CLOSE].pct_change(window) * 100
    data = data.dropna()
    return data

"""Generates a dataframe with rolling returns for multiple leverages."""
def generate_rolling_returns_multiple_leverages(reference_data: DataFrame, *, leverages: list[float], mers: list[float], window=2520, initial_value=1.0) -> DataFrame:
    data = reference_data.copy()
    data = hist.compute_multiple_leverages(data, leverages=leverages, mers=mers, initial_value=initial_value)
    
    data[hist.Columns.CLOSE] = data[hist.Columns.CLOSE].pct_change(window) * 100
    for leverage in leverages:
        lev_close = hist.column_prefixer(hist.Columns.LEV_CLOSE, leverage)
        adj_close = hist.column_prefixer(hist.Columns.ADJ_CLOSE, leverage)
        data[lev_close] = data[lev_close].pct_change(window) * 100
        data[adj_close] = data[adj_close].pct_change(window) * 100
    data = data.dropna()
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
    leverage_factor = 3.0
    mer = 0.01
    initial_value = 1.0
    window = 252 * 30    # there are 252 business days in a year

    for name, ticker in indices.items():
        # Step 1: Download historical data
        reference_data = hist.download_data(ticker, start=start_date, end=end_date)
        if reference_data.empty:
            continue
        
        # Step 2: Compute rolling returns for the specified length of time
        rolling_data = generate_rolling_returns(reference_data, window=window, initial_value=initial_value, mer=mer, leverage=leverage_factor)
        
        print(f"Data for {name}:")
        print(rolling_data)
        
        # Step 3: Plot the results
        title = f'{round(window / 252)} Year Rolling Returns for {name} Index'
        hist.plot_data(rolling_data, title=title, leverage=leverage_factor, y_axis='Return')
        
        # Step 6: Compare multiple leverages (MER adjusted)
        levs = [2.0, 3.0]
        mers = [0.01, 0.01]
        rolling_data = generate_rolling_returns_multiple_leverages(reference_data, window=window, leverages=levs, mers=mers, initial_value=initial_value)
        hist.plot_multiple_leverage(rolling_data, leverages=levs, title=title, y_axis='Return')

if __name__ == "__main__":
    main()
