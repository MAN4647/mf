import pandas as pd
import requests
from io import StringIO

#Download the raw text file
url = 'https://www.amfiindia.com/spages/NAVAll.txt'
response = requests.get(url)
text = response.text

#Split into lines and find the actual data starting point
lines = text.splitlines()
# Remove empty lines and header lines
data_lines = [line for line in lines if ';' in line and not line.startswith("Scheme Code")]

#Recreate the data as a single string for pandas
data_str = '\n'.join(data_lines)

#Convert to DataFrame
df = pd.read_csv(StringIO(data_str), sep=';', header=None)

#Assign proper column names
df.columns = [
    "Scheme Code", "ISIN Div Payout/ISIN Growth", "ISIN Div Reinvestment",
    "Scheme Name", "Net Asset Value", "Date"
]
 
# Step 6: Clean up data types
df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y', errors='coerce')
df['Net Asset Value'] = pd.to_numeric(df['Net Asset Value'], errors='coerce')

df.to_excel("output.xlsx", sheet_name="Sheet1", index=False)
print("Saved to output.xlsx")