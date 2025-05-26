import yfinance as yf
import time

def fetch_market_data(symbols, indices=None, currencies=None, commodities=None):
    data = {"stocks": {}, "indices": {}, "currencies": {}, "commodities": {}}
    
    # Fetch stock data
    for symbol in symbols:
        time.sleep(1)  # Avoid rate limits
        stock = yf.Ticker(symbol)
        info = stock.info
        data["stocks"][symbol] = {
            "price": info.get("regularMarketPrice", 0),
            "eps_actual": info.get("trailingEps", 0),
            "eps_estimate": info.get("forwardEps", 0)
        }
    
    # Fetch indices
    if indices:
        for index in indices:
            time.sleep(1)
            ticker = yf.Ticker(index)
            info = ticker.info
            data["indices"][index] = info.get("regularMarketChangePercent", 0)
    
    # Fetch currencies (e.g., USD/EUR)
    if currencies:
        for currency in currencies:
            time.sleep(1)
            ticker = yf.Ticker(currency + "=X")
            info = ticker.info
            data["currencies"][currency] = info.get("regularMarketChangePercent", 0)
    
    # Fetch commodities
    if commodities:
        for commodity in commodities:
            time.sleep(1)
            ticker = yf.Ticker(commodity)
            info = ticker.info
            data["commodities"][commodity] = info.get("regularMarketChangePercent", 0)
    
    return data