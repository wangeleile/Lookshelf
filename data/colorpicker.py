from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import requests
from io import BytesIO
import yaml
import os

# Hilfsfunktion: Dominierende Farbe aus Bild-URL bestimmen (HEX)
def get_dominant_color_hex(url):
    try:
        response = requests.get(url, timeout=10)
        image = Image.open(BytesIO(response.content)).convert('RGB')
        image = image.resize((100, 100))
        data = np.array(image)
        data = data.reshape((-1, 3))
        kmeans = KMeans(n_clusters=1, n_init=3)
        kmeans.fit(data)
        color = kmeans.cluster_centers_[0].astype(int)
        # HEX-Format
        return '#{:02X}{:02X}{:02X}'.format(color[0], color[1], color[2])
    except Exception as e:
        print(f"Fehler bei Bild {url}: {e}")
        return None

# YAML laden
input_path = 'data/Meine_Buchliste.yaml'
output_path = 'data/Meine_Buchliste.yaml'

with open(input_path, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

# Bücher iterieren und Farbe setzen
for book in data.get('books', []):
    url = book.get('image_url')
    if url:
        color = get_dominant_color_hex(url)
        if color:
            book['book_color'] = color
        else:
            book['book_color'] = None
    else:
        book['book_color'] = None

# YAML speichern
with open(output_path, 'w', encoding='utf-8') as f:
    yaml.dump(data, f, allow_unicode=True, sort_keys=False)

print(f"Fertig! Neue Datei: {output_path}")