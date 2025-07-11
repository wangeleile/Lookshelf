from PIL import Image
import numpy as np
from sklearn.cluster import KMeans

# Bild laden
image = Image.open('https://books.google.com/books/content?id=7notgaTVUFAC&printsec=frontcover&img=1&zoom=5&edge=curl&source=gbs_api')
image = image.resize((100, 100))  # Verkleinern für schnellere Verarbeitung
data = np.array(image)
data = data.reshape((-1, 3))

# KMeans-Clustering, um dominante Farben zu finden
kmeans = KMeans(n_clusters=1)
kmeans.fit(data)
dominant_color = kmeans.cluster_centers_[0].astype(int)

print("Dominierende Farbe (RGB):", dominant_color)