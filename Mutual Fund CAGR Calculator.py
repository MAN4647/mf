import pandas as pd
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# HTML template for the frontend
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mutual Fund CAGR Calculator</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            padding: 25px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 20px;
            text-align: center;
        }
        .input-group {
            display: flex;
            margin-bottom: 20px;
        }
        input {
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px 0 0 4px;
            font-size: 16px;
        }
        button {
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 0 4px 4px 0;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        .scheme-info {
            margin-bottom: 20px;
            font-size: 18px;
            color: #2c3e50;
            background-color: #ecf0f1;
            padding: 10px;
            border-radius: 4px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
            font-weight: 600;
        }
        .positive {
            color: green;
            font-weight: bold;
        }
        .negative {
            color: red;
            font-weight: bold;
        }
        .loading {
            text-align: center;
            margin: 20px 0;
            font-style: italic;
            color: #7f8c8d;
        }
        .error {
            color: #e74c3c;
            padding: 10px;
            margin-top: 10px;
            border-radius: 4px;
            background-color: #fadbd8;
        }
        .hidden {
            display: none;
        }
        .note {
            font-size: 14px;
            color: #7f8c8d;
            margin-top: 20px;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Mutual Fund CAGR Calculator</h1>
        
        <div class="input-group">
            <input type="text" id="scheme-code" placeholder="Enter Scheme Code (e.g., 118834)">
            <button id="calculate-btn">Calculate</button>
        </div>
        
        <div id="error-message" class="error hidden"></div>
        
        <div id="loading" class="loading hidden">Fetching data and calculating returns...</div>
        
        <div id="results" class="hidden">
            <div id="scheme-info" class="scheme-info"></div>
            
            <table>
                <thead>
                    <tr>
                        <th>Time Period</th>
                        <th>CAGR</th>
                    </tr>
                </thead>
                <tbody id="results-table">
                    <!-- Results will be populated here -->
                </tbody>
            </table>
        </div>
        
        <div class="note">
            <strong>Data source:</strong> This calculator uses data from MFAPI.in. The calculations are done on the server.
        </div>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const calculateBtn = document.getElementById('calculate-btn');
            const schemeCodeInput = document.getElementById('scheme-code');
            const resultsDiv = document.getElementById('results');
            const schemeInfoDiv = document.getElementById('scheme-info');
            const resultsTable = document.getElementById('results-table');
            const loadingDiv = document.getElementById('loading');
            const errorMessageDiv = document.getElementById('error-message');
            
            calculateBtn.addEventListener('click', calculateCAGR);
            schemeCodeInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    calculateCAGR();
                }
            });
            
            function calculateCAGR() {
                const schemeCode = schemeCodeInput.value.trim();
                
                if (!schemeCode) {
                    showError('Please enter a scheme code');
                    return;
                }
                
                showLoading();
                
                fetch('/calculate-cagr/' + schemeCode)
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            throw new Error(data.error);
                        }
                        displayResults(data);
                    })
                    .catch(error => {
                        showError(`Error: ${error.message || 'Failed to fetch data'}`);
                    });
            }
            
            function displayResults(data) {
                schemeInfoDiv.textContent = `Scheme: ${data.scheme_name}`;
                
                resultsTable.innerHTML = '';
                
                const periods = [
                    { name: '1 Month', value: data.cagr_1m },
                    { name: '1 Year', value: data.cagr_1y },
                    { name: '3 Years', value: data.cagr_3y },
                    { name: '5 Years', value: data.cagr_5y },
                    { name: 'Lifetime', value: data.cagr_lifetime }
                ];
                
                periods.forEach(period => {
                    const row = document.createElement('tr');
                    
                    const periodCell = document.createElement('td');
                    periodCell.textContent = period.name;
                    row.appendChild(periodCell);
                    
                    const valueCell = document.createElement('td');
                    if (period.value === null) {
                        valueCell.textContent = 'Insufficient data';
                    } else {
                        const formattedValue = period.value.toFixed(2) + '%';
                        valueCell.textContent = formattedValue;
                        valueCell.className = period.value >= 0 ? 'positive' : 'negative';
                    }
                    row.appendChild(valueCell);
                    
                    resultsTable.appendChild(row);
                });
                
                hideLoading();
                resultsDiv.classList.remove('hidden');
            }
            
            function showLoading() {
                errorMessageDiv.classList.add('hidden');
                resultsDiv.classList.add('hidden');
                loadingDiv.classList.remove('hidden');
            }
            
            function hideLoading() {
                loadingDiv.classList.add('hidden');
            }
            
            function showError(message) {
                errorMessageDiv.textContent = message;
                errorMessageDiv.classList.remove('hidden');
                resultsDiv.classList.add('hidden');
                loadingDiv.classList.add('hidden');
            }
        });
    </script>
</body>
</html>
"""

def calculate_cagr(df, from_date, to_date):
    """Calculate the CAGR for a given date range."""
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

@app.route('/')
def index():
    """Render the main page."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/calculate-cagr/<scheme_code>')
def get_cagr(scheme_code):
    """Calculate CAGR for a given scheme code."""
    try:
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
        
        # Calculate current date and relevant historical dates
        current_date = datetime.now()
        one_month_ago = current_date - timedelta(days=30)
        one_year_ago = current_date - timedelta(days=365)
        three_year_ago = current_date - timedelta(days=365 * 3)
        five_year_ago = current_date - timedelta(days=365 * 5)
        
        # Calculate CAGR for various periods
        cagr_1m = calculate_cagr(nav_data, one_month_ago, current_date)
        cagr_1yr = calculate_cagr(nav_data, one_year_ago, current_date)
        cagr_3yr = calculate_cagr(nav_data, three_year_ago, current_date)
        cagr_5yr = calculate_cagr(nav_data, five_year_ago, current_date)
        cagr_lifetime = calculate_cagr(nav_data, nav_data['date'].min(), nav_data['date'].max())
        
        # Prepare result
        result = {
            'scheme_name': data['meta']['scheme_name'],
            'cagr_1m': None if cagr_1m is None else cagr_1m * 100,
            'cagr_1y': None if cagr_1yr is None else cagr_1yr * 100,
            'cagr_3y': None if cagr_3yr is None else cagr_3yr * 100,
            'cagr_5y': None if cagr_5yr is None else cagr_5yr * 100,
            'cagr_lifetime': None if cagr_lifetime is None else cagr_lifetime * 100
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

    