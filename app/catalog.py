import requests

# Fetch JSON from URL
response = requests.get("https://tcp-us-prod-rnd.shl.com/voiceRater/shl-ai-hiring/shl_product_catalog.json")

# Save to file
with open("data/catalog.json", "w") as f:
    f.write(response.text)

print("Catalog saved!")