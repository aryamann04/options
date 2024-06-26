import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from datetime import datetime

# Get current treasury yields from CNBC
def treasury_yield(t):
    url = get_url(t)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    container = soup.find('div', class_='QuoteStrip-lastPriceStripContainer')
    if container:
        yield_element = container.find('span', class_='QuoteStrip-lastPrice')
        if yield_element:
            yield_value = yield_element.text.strip()
            return float(yield_value.replace('%', '')) / 100
        else:
            print("Yield span not found.")
            return None
    else:
        print("Yield container not found.")
        return None

def get_url(t):
    times = {
        '1M': 1 / 12,  # 1 month
        '2M': 2 / 12,  # 2 months
        '3M': 3 / 12,  # 3 months
        '4M': 4 / 12,  # 4 months
        '6M': 6 / 12,  # 6 months
        '1Y': 1,  # 1 year
        '2Y': 2,  # 2 years
        '3Y': 3,  # 3 years
        '5Y': 5,  # 5 years
        '7Y': 7,  # 7 years
        '10Y': 10,  # 10 years
        '20Y': 20,  # 20 years
        '30Y': 30  # 30 years
    }
    closest = min(times.keys(), key=lambda k: abs(times[k] - t))
    return 'https://www.cnbc.com/quotes/US' + closest

# Method to plot the current yield curve
def plot_yield_curve():
    maturities = ['1M', '2M', '3M', '4M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y']
    times = [1 / 12, 2 / 12, 3 / 12, 4 / 12, 6 / 12, 1, 2, 3, 5, 7, 10, 20, 30]
    yields = []

    for maturity in maturities:
        yield_value = treasury_yield(times[maturities.index(maturity)])
        if yield_value is not None:
            yields.append(yield_value)
        else:
            yields.append(0)  # Append 0 if the yield is not found

    # Get today's date
    today = datetime.today().strftime('%Y-%m-%d')

    plt.figure(figsize=(10, 6))
    plt.plot(maturities, yields, marker='o')
    plt.title(f'Current Treasury Yield Curve as of {today}')
    plt.xlabel('Maturity')
    plt.ylabel('Yield')

    # Format y-axis as percentage
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.2%}'))

    plt.grid(True)
    plt.show()
