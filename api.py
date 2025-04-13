import pandas as pd
import requests
from datetime import datetime, timedelta

# Example: Axis Bluechip Fund (Growth)
scheme_code = '147946'  # You can find code from MFAPI.in

url = f'https://api.mfapi.in/mf/{scheme_code}'
response = requests.get(url)
data = response.json()

# Convert to DataFrame
nav_data = pd.DataFrame(data['data'])

# Add scheme code and scheme name
nav_data['scheme_code'] = scheme_code
nav_data['scheme_name'] = data['meta']['scheme_name']

# Convert NAV and date to proper types
nav_data['nav'] = pd.to_numeric(nav_data['nav'], errors='coerce')
nav_data['date'] = pd.to_datetime(nav_data['date'], format='%d-%m-%Y')

# Sort by date
nav_data = nav_data.sort_values('date')
# print(nav_data.head())

current_date = datetime.strptime("2025-04-11", "%Y-%m-%d")
one_month_ago = current_date - timedelta(days=31)
one_year_ago = current_date - timedelta(days=365)
three_year_ago = current_date - timedelta(days=365 * 3)
five_year_ago = current_date - timedelta(days=365 * 5)

def calculate_cagr(df, from_date, to_date):
    df_range = df[(df['date'] >= from_date) & (df['date'] <= to_date)].sort_values('date')
    if df_range.empty:
        return None
    initial_nav = df_range.iloc[0]['nav']
    final_nav = df_range.iloc[-1]['nav']
    days = (df_range.iloc[-1]['date'] - df_range.iloc[0]['date']).days
    years = days / 365.0
    if years == 0 or initial_nav == 0:
        return None
    return ((final_nav / initial_nav) ** (1 / years)) - 1

cagr_1yr = calculate_cagr(nav_data, one_year_ago, current_date)
cagr_3yr = calculate_cagr(nav_data, three_year_ago, current_date)
cagr_5yr = calculate_cagr(nav_data, five_year_ago, current_date)
cagr_lifetime = calculate_cagr(nav_data, nav_data['date'].min(), nav_data['date'].max())

print("CAGR 1Y:", round(cagr_1yr * 100, 2), "%")
print("CAGR 3Y:", round(cagr_3yr * 100, 2), "%")
print("CAGR 5Y:", round(cagr_5yr * 100, 2), "%")
print("CAGR Lifetime:", round(cagr_lifetime * 100, 2), "%")