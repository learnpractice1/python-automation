
stock_data1 = {
"KALYANKJIL": 0, "GODREJPROP": 0, "HUDCO": 0, "HDFCLIFE": 0, "JIOFIN": 0, "PATANJALI": 0, "ITC": 0, "IREDA": 0, "ASIANPAINT": 0, "PAYTM": 0, "TATACONSUM": 0, "SBICARD": 0, "SYNGENE": 0, "KFINTECH": 0,
}
expiry_date="30-Mar-2026"

stock_data = {}  # Final dictionary
error_symbols = []

import pandas as pd
from nsepythonserver import *
import pandas as pd
import time
import random

## for only put and depending decide a range
def find_most_active_strike(df, current_price):
    pct_range = 0.07
    upper_range=0.03 ### this is an optional thing for running 

    # Ensure numeric types
    df['CALLS_OI'] = pd.to_numeric(df['CALLS_OI'], errors='coerce')
    df['PUTS_OI'] = pd.to_numeric(df['PUTS_OI'], errors='coerce')
    df['CALLS_Volume'] = pd.to_numeric(df['CALLS_Volume'], errors='coerce')
    df['PUTS_Volume'] = pd.to_numeric(df['PUTS_Volume'], errors='coerce')
    df['Strike Price'] = pd.to_numeric(df['Strike Price'], errors='coerce')

    # Fill NaNs with 0
    df.fillna(0, inplace=True)

    # Define range
    # can be varaible depending upon what we need especially the upper_bound and lower_bound values
    lower_bound = current_price * (1 - pct_range)
    upper_bound = current_price* (1 - upper_range)

    # Filter strikes within range and make a copy to avoid SettingWithCopyWarning
    df_range = df[(df['Strike Price'] >= lower_bound) & (df['Strike Price'] <= upper_bound)].copy()

    if df_range.empty:
        return None  # No strikes in range

    # Calculate total OI and Volume
    df_range['Total_OI'] = df_range['CALLS_OI'] + df_range['PUTS_OI']
    df_range['Total_Volume'] = df_range['CALLS_Volume'] + df_range['PUTS_Volume']
    df_range['Activity_Score'] = df_range['Total_OI'] + df_range['Total_Volume']

    # Find strike with highest activity
    most_active = df_range.loc[df_range['Activity_Score'].idxmax()]
    return most_active['Strike Price']

## fetching data from nse website
def option_chain_data_pull(stock_name, expiry_date):
  a=nsefetch(f"https://www.nseindia.com/api/NextApi/apiClient/GetQuoteApi?functionName=getOptionChainData&symbol={stock_name}&params=expiryDate={expiry_date}")
  current_price=a['underlyingValue']
  opt_chain=create_option_chain_df(a['data'])
  return opt_chain,current_price

### getting values from optios chain which we fetched from  option_chain_data_pull functions
def create_option_chain_df(option_data):
    option_chain = []

    for item in option_data:
        strike_price = item.get('strikePrice')
        ce_data = item.get('CE', {})
        pe_data = item.get('PE', {})

        row = {
            'Strike Price': strike_price,
            'CALLS_OI': ce_data.get('openInterest'),
            'CE_Change_in_OI': ce_data.get('changeinOpenInterest'),
            'CALLS_Volume': ce_data.get('totalTradedVolume'),
            'CE_IV': ce_data.get('impliedVolatility'),
            'CE_Last_Price': ce_data.get('lastPrice'),
            'CE_Change': ce_data.get('change'),
            'PUTS_OI': pe_data.get('openInterest'),
            'PE_Change_in_OI': pe_data.get('changeinOpenInterest'),
            'PUTS_Volume': pe_data.get('totalTradedVolume'),
            'PE_IV': pe_data.get('impliedVolatility'),
            'PE_Last_Price': pe_data.get('lastPrice'),
            'PE_Change': pe_data.get('change'),
        }
        option_chain.append(row)

    return pd.DataFrame(option_chain)

# To track symbols that raise errors
# main function

for symbol, value in stock_data1.items():
    try:
        delay = random.uniform(1, 3)
        time.sleep(delay)  # Add delay
        opt_data,crt_data = option_chain_data_pull(symbol,expiry_date)  # Your custom function
        active_stike=find_most_active_strike(opt_data,crt_data)
        stock_data[symbol] = active_stike
    except Exception as e:
        print(f"Error with symbol: {symbol} → {e}")
        error_symbols.append(symbol)

stock_data_standard_float = {k: float(v) for k, v in stock_data.items()}
stock_data_standard_float

# Save stock data to Excel
df = pd.DataFrame(list(stock_data_standard_float.items()), columns=["Ticker", "Value"])
df.to_excel("stock_data.xlsx", index=False)

# Save error symbols to a separate file
if error_symbols:
    pd.DataFrame(error_symbols, columns=["Error_Ticker"]).to_csv("error_symbols.csv", index=False)
