import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.config import TOP_K

# Load FAISS index and embeddings
index = faiss.read_index("data/catalog.faiss")
embeddings = np.load("data/embeddings.npy")

# Load catalog
with open("data/catalog.json", encoding='utf-8') as f:
    catalog = json.load(f)

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Query
query = "Hiring Java developer 4 years client communication"
query_vector = model.encode(query, normalize_embeddings=True).astype('float32').reshape(1, -1)

# Search
distances, indices = index.search(query_vector, k=TOP_K)

print(f"Query: {query}\n")
print(f"Indices I\n{indices}\n")
print(f"Distances D\n{distances}")
