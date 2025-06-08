from flask import Flask, jsonify, request
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin frontend requests

@app.route('/define/<word>')
def define(word):
    # Optional query param `limit` to cap number of definitions
    limit = request.args.get('limit', type=int)

    url = f"https://www.wordreference.com/fren/{word}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return jsonify({"error": "Failed to fetch definition"}), 500

    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table', {'class': 'WRD'})
    results = []

    if table:
        for row in table.find_all('tr', recursive=False):
            # Only process rows with class 'even' or 'odd'
            if any(c in ['even','odd'] for c in row.get('class', [])):
                fr_td = row.find('td', class_='FrWrd')
                en_td = row.find('td', class_='ToWrd')
                if not (fr_td and en_td):
                    continue

                # Clean French word (prefer <strong> tag)
                french = (
                    fr_td.find('strong').get_text(strip=True)
                    if fr_td.find('strong') else fr_td.get_text(strip=True)
                )

                # Clean English word, strip POS suffixes
                raw_en = en_td.get_text(strip=True)
                clean_en = re.sub(
                    r'(interj|n|v|adj|adv|prep|conj|pron|expr)$',
                    '',
                    raw_en,
                    flags=re.IGNORECASE
                ).strip()

                results.append({"french": french, "english": clean_en})

                # Stop if we've reached the requested limit
                if limit is not None and len(results) >= limit:
                    break

    return jsonify(results if results else {"error": "No results found"})