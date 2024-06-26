import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def get_iv(tic, K, T, option_type):
    ticker = yf.Ticker(tic)
    K = 5 * round(K / 5)  # Round strike to nearest 5 for finding market prices
    exp_dates = ticker.options
    target_expiry = datetime.now() + timedelta(days=T * 365)
    closest_expiry = min(exp_dates, key=lambda x: abs(datetime.strptime(x, '%Y-%m-%d') - target_expiry))

    option_chain = ticker.option_chain(date=closest_expiry)
    if option_type == "call":
        options = option_chain.calls
    else:
        options = option_chain.puts

    option_row = options[options['strike'] == K]
    if option_row.empty:
        return None
    else:
        return option_row['impliedVolatility'].values[0]

def vol_skew(ticker, expiry_years, strike):
    today = datetime.today()
    expiry_date = today + timedelta(days=expiry_years * 365)
    ticker_obj = yf.Ticker(ticker)
    options = ticker_obj.options

    if not options:
        raise ValueError(f"No options data available for ticker {ticker}")

    option_dates = [datetime.strptime(exp_date, '%Y-%m-%d') for exp_date in options]
    expiry_date_str = min(option_dates, key=lambda x: abs(x - expiry_date)).strftime('%Y-%m-%d')

    option_chain = ticker_obj.option_chain(date=expiry_date_str)
    vol_at_strike = get_iv(ticker, strike, expiry_years, 'call')
    if vol_at_strike is None:
        raise ValueError(f"No implied volatility data available for strike {strike}")

    lower_strike = strike - 5
    vol_lower = get_iv(ticker, lower_strike, expiry_years, 'call')
    if vol_lower is None:
        raise ValueError(f"No implied volatility data available for strike {lower_strike}")

    upper_strike = strike + 5
    vol_upper = get_iv(ticker, upper_strike, expiry_years, 'call')
    if vol_upper is None:
        raise ValueError(f"No implied volatility data available for strike {upper_strike}")
    skew = (vol_upper - vol_lower) / (upper_strike - lower_strike)
    return skew

def get_expiry_date(ticker, expiry_years):
    today = datetime.today()
    expiry_date = today + timedelta(days=expiry_years * 365)
    ticker_obj = yf.Ticker(ticker)
    options = ticker_obj.options
    if not options:
        raise ValueError(f"No options data available for ticker {ticker}")
    option_dates = [datetime.strptime(exp_date, '%Y-%m-%d') for exp_date in options]
    expiry_date_str = min(option_dates, key=lambda x: abs(x - expiry_date)).strftime('%Y-%m-%d')

    return expiry_date_str

def plot_vol_skew(ticker, expiry_years):
    today = datetime.today()
    expiry_date = today + timedelta(days=expiry_years * 365)

    ticker_obj = yf.Ticker(ticker)
    options = ticker_obj.options

    if not options:
        raise ValueError(f"No options data available for ticker {ticker}")

    option_dates = [datetime.strptime(exp_date, '%Y-%m-%d') for exp_date in options]
    expiry_date_str = min(option_dates, key=lambda x: abs(x - expiry_date)).strftime('%Y-%m-%d')

    option_chain = ticker_obj.option_chain(date=expiry_date_str)
    calls = option_chain.calls

    strikes = calls['strike'].values
    implied_vols = calls['impliedVolatility'].values

    valid_indices = implied_vols != 0
    strikes = strikes[valid_indices]
    implied_vols = implied_vols[valid_indices]

    filtered_strikes = []
    filtered_vols = []
    for i in range(len(strikes)):
        if implied_vols[i] != 0:
            filtered_strikes.append(strikes[i])
            filtered_vols.append(implied_vols[i])
        elif filtered_vols:
            filtered_strikes.append(None)
            filtered_vols.append(None)

    fig, ax = plt.subplots()
    ax.plot(filtered_strikes, filtered_vols, label='Implied Volatility', marker='o', linestyle='-')

    ax.set_xlabel('Strike Prices')
    ax.set_ylabel('Implied Volatility')
    ax.set_title(f'Volatility Skew for {ticker} on {expiry_date_str}')
    ax.legend()
    ax.grid(True)

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

plot_vol_skew("AAPL", 0.5)
