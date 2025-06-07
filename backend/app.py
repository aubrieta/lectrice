from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)
CORS(app)  # Enable cross-origin requests from frontend

@app.route('/define/<word>')
def define(word):
    limit = request.args.get('limit', type=int)
    url = f"https://www.wordreference.com/fren/{word}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return jsonify({"error": "Failed to fetch definition"}), 500
    except Exception as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 500

    soup = BeautifulSoup(r.text, 'html.parser')
    tables = soup.find_all('table', {'class': 'WRD'})
    results = []

    for table in tables:
        for row in table.find_all('tr', recursive=False):
            if any(c in ['even', 'odd'] for c in row.get('class', [])):
                fr_td = row.find('td', class_='FrWrd')
                en_td = row.find('td', class_='ToWrd')
                if not (fr_td and en_td):
                    continue

                # Clean French entry
                french = (
                    fr_td.find('strong').get_text(strip=True)
                    if fr_td.find('strong')
                    else fr_td.get_text(strip=True)
                )

                # Clean English entry — remove POS suffix if present
                raw_en = en_td.get_text(strip=True)
                clean_en = re.sub(
                    r'(interj|n|v|adj|adv|prep|conj|pron|expr|vi|vtr)[.,\s]*$',
                    '',
                    raw_en,
                    flags=re.IGNORECASE
                ).strip()

                results.append({"french": french, "english": clean_en})

                if limit is not None and len(results) >= limit:
                    return jsonify(results)

    return jsonify(results if results else {"error": "No results found"})
