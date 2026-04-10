import json
import os
from store import LawVectorStore

def main():
    chunks_path = "law_chunks.json"
    if not os.path.exists(chunks_path):
        print(f"Error: {chunks_path} not found. Please run the parser first.")
        return
        
    print(f"Loading chunks from {chunks_path}...")
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
        
    print(f"Found {len(chunks)} chunks.")
    
    # Initialize and build store
    store = LawVectorStore()
    store.create_index(chunks)
    
    # Save the store
    store.save("store")
    print("Vector store build complete.")

if __name__ == "__main__":
    main()
