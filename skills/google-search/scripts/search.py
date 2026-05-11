import sys
import json
import requests
import os

def google_search(query, api_key, cse_id, num_results=5):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': query,
        'key': api_key,
        'cx': cse_id,
        'num': num_results
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python google_search.py <query> [num_results]")
        sys.exit(1)

    query = sys.argv[1]
    num_results = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    # We will pass these via env vars for security
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")

    if not api_key or not cse_id:
        print("Error: GOOGLE_API_KEY and GOOGLE_CSE_ID must be set in environment.")
        sys.exit(1)

    try:
        results = google_search(query, api_key, cse_id, num_results)
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
