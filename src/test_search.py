from store import LawVectorStore
import json
import sys

# Configure stdout for UTF-8 to avoid encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_search():
    store = LawVectorStore()
    if not store.load("store"):
        print("Failed to load store.")
        return
        
    query = "trách nhiệm dân sự của cá nhân"
    print(f"Testing search for: '{query}'")
    results = store.search(query, top_k=3)
    
    for i, res in enumerate(results):
        print(f"\nResult {i+1} (Score: {res['score']:.4f}):")
        content = res['content']
        print(f"Location: {content['metadata']}")
        # Print first 200 chars of text
        print(f"Text snippet: {content['text'][:200]}...")

if __name__ == "__main__":
    test_search()
