from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend on different origin

@app.route('/define/<word>')
def define(word):
    url = f"https://www.wordreference.com/fren/{word}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return jsonify({"error": "Failed to fetch definition"}), 500

    soup = BeautifulSoup(r.text, 'html.parser')
    results = []
    table = soup.find('table', {'class': 'WRD'})

    if table:
        rows = table.find_all('tr', recursive=False)
        for row in rows:
            if 'class' in row.attrs and ('even' in row['class'] or 'odd' in row['class']):
                fr = row.find('td', class_='FrWrd')
                en = row.find('td', class_='ToWrd')
                if fr and en:
                    results.append({
                        "french": fr.find('strong').get_text(strip=True) if fr.find('strong') else fr.get_text(strip=True),
                        "english": en.find('strong').get_text(strip=True) if en.find('strong') else en.get_text(strip=True)
                    })
            if len(results) >= 3:
                break

    return jsonify(results if results else {"error": "No results found"})
