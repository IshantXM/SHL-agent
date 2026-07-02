import json
import faiss
import numpy as np
import logging
from sentence_transformers import SentenceTransformer

# Suppress warnings
logging.disable(logging.CRITICAL)

# Load catalog
with open("data/catalog.json", encoding='utf-8') as f:
    catalog = json.load(f)

documents = []

for item in catalog:
    text = f"""
    {item['name']}
    {item['description']}
    """
    documents.append(text)

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
embeddings = model.encode(
    documents,
    normalize_embeddings=True
)

embeddings = np.array(embeddings, dtype=np.float32)

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

# Save index and embeddings
faiss.write_index(index, "data/catalog.faiss")
np.save("data/embeddings.npy", embeddings)

print(f"✓ Saved catalog.faiss")
print(f"✓ Saved embeddings.npy")
print(f"✓ Total documents: {len(documents)}")
print(f"✓ Embedding dimensions: {embeddings.shape[1]}")