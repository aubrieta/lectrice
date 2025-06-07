from flask import Flask, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)
CORS(app)  # Enable CORS so frontend (on GitHub Pages) can call this

@app.route('/define/<word>')
def define(word):
    url = f"https://www.wordreference.com/fren/{word}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return jsonify({"error": "Failed to fetch definition"}), 500

    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table', {'class': 'WRD'})
    results = []

    if table:
        rows = table.find_all('tr', recursive=False)
        for row in rows:
            if 'class' in row.attrs and ('even' in row['class'] or 'odd' in row['class']):
                fr = row.find('td', class_='FrWrd')
                en = row.find('td', class_='ToWrd')

                if fr and en:
                    # Extract French word (strong tag preferred)
                    french = fr.find('strong').get_text(strip=True) if fr.find('strong') else fr.get_text(strip=True)

                    # Extract English word, stripping off POS tags like "interj.", "n.", "v.", etc.
                    raw_en = en.get_text(strip=True)
                    clean_en = re.split(r'\b(?:n|v|adj|adv|interj|prep|conj|pron|expr)\b\.?', raw_en, maxsplit=1)[0].strip()

                    results.append({
                        "french": french,
                        "english": clean_en
                    })

            if len(results) >= 3:
                break

    return jsonify(results if results else {"error": "No results found"})
