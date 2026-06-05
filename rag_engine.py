import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import google.generativeai as genai

def load_dotenv():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(script_dir, ".env"),
        os.path.join(os.getcwd(), ".env"),
        ".env"
    ]
    for env_path in possible_paths:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            parts = line.split("=", 1)
                            if len(parts) == 2:
                                k, v = parts
                                k = k.strip()
                                v = v.strip().strip("'\"")
                                os.environ[k] = v
                break
            except Exception as e:
                pass

# Load environment variables
load_dotenv()

# List of fund identifiers to help with strict routing/filtering
FUND_MAPPING = {
    "large_midcap": {
        "keywords": ["large and midcap", "large & midcap", "large and mid cap", "large mid cap", "large midcap"]
    },
    "multicap_35": {
        "keywords": ["multicap 35", "multi cap 35", "most focused multicap 35", "focused 35"]
    },
    "momentum": {
        "keywords": ["active momentum", "momentum", "momentum fund"]
    },
    "multicap": {
        "keywords": ["multi cap", "multicap", "multi-cap"]
    },
    "long_term": {
        "keywords": ["long term", "long-term", "focused long term", "elss", "tax saver"]
    },
    "contra": {
        "keywords": ["contra", "contra fund"]
    },
    "digital_india": {
        "keywords": ["digital india", "digital", "digital fund", "it fund", "technology fund"]
    },
    "bse_enhanced_value": {
        "keywords": ["bse enhanced value", "enhanced value", "bse value"]
    },
    "gold_silver": {
        "keywords": ["gold and silver", "gold & silver", "passive fof", "gold silver"]
    },
    "midcap_30": {
        "keywords": ["focused midcap 30", "midcap 30", "focused midcap"]
    },
    "nifty_500": {
        "keywords": ["nifty 500 index", "nifty 500 fund", "nifty 500"]
    },
    "nifty_500_momentum": {
        "keywords": ["nifty 500 momentum", "momentum 50 index", "momentum 50"]
    },
    "nifty_capital": {
        "keywords": ["nifty capital market", "capital market index", "capital market fund"]
    },
    "nifty_defence": {
        "keywords": ["nifty india defence", "nifty defence", "defence index", "defence fund"]
    },
    "nifty_midcap": {
        "keywords": ["nifty midcap 150", "midcap 150 index", "midcap 150 fund"]
    },
    "small_cap": {
        "keywords": ["small cap fund", "small cap", "smallcap"]
    }
}

class RAGEngine:
    def __init__(self, chunks_path=os.path.join("data", "chunks.json")):
        self.chunks_path = chunks_path
        self.chunks = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self.embeddings = None
        self.api_key_configured = False
        
        # Configure Gemini if key is present
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.api_key_configured = True
            
        self.load_chunks()
        self.build_index()

    def load_chunks(self):
        if not os.path.exists(self.chunks_path):
            print(f"Warning: Chunks file {self.chunks_path} not found. Please run ingestion first.")
            return
            
        with open(self.chunks_path, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)
            
        print(f"Loaded {len(self.chunks)} pre-computed semantic chunks.")

    def normalize(self, vectors):
        norms = np.linalg.norm(vectors, axis=-1, keepdims=True)
        return vectors / np.maximum(norms, 1e-12)

    def build_index(self):
        if not self.chunks:
            return
            
        # 1. Initialize TF-IDF for keyword matching (runs locally, zero DLL dependencies)
        self.vectorizer = TfidfVectorizer(stop_words='english', token_pattern=r'(?u)\b\w+\b')
        chunk_texts = [chunk["content"] for chunk in self.chunks]
        self.tfidf_matrix = self.vectorizer.fit_transform(chunk_texts)
        
        # 2. Compute cloud-based Gemini embeddings if API key is present
        if self.api_key_configured:
            print("GEMINI_API_KEY found. Pre-computing Gemini cloud embeddings (models/text-embedding-004)...")
            try:
                # Batch embed chunks
                response = genai.embed_content(
                    model="models/text-embedding-004",
                    contents=chunk_texts
                )
                self.embeddings = self.normalize(np.array(response["embedding"]))
                print("Gemini Semantic Embeddings index built successfully.")
            except Exception as e:
                print(f"Error computing Gemini embeddings: {e}. Falling back to TF-IDF only.")
                self.embeddings = None
        else:
            print("No GEMINI_API_KEY found. Running in local TF-IDF keyword search mode.")
            self.embeddings = None

    def detect_fund_filter(self, query):
        """
        Detects if the query refers to a specific fund and returns its tag,
        or None if it's general or refers to multiple.
        """
        query_lower = query.lower().strip()
        
        # Check specifically for "multicap 35" first to avoid colliding with "multicap"
        if any(keyword in query_lower for keyword in FUND_MAPPING["multicap_35"]["keywords"]):
            return "multicap_35"
            
        for tag, info in FUND_MAPPING.items():
            if tag == "multicap_35":
                continue # Already handled
            if any(keyword in query_lower for keyword in info["keywords"]):
                return tag
                
        return None

    def retrieve(self, query, top_k=4):
        if not self.chunks:
            return []
            
        # Detect fund filter
        fund_filter = self.detect_fund_filter(query)
        print(f"Query: '{query}' | Detected Filter: {fund_filter}")
        
        # Filter chunks candidates
        candidates = []
        candidate_indices = []
        
        for idx, chunk in enumerate(self.chunks):
            # If a specific fund is requested, limit to that fund's chunks AND general AMC chunks
            if fund_filter:
                if chunk["fund_tag"] == fund_filter or chunk["fund_tag"] == "amc":
                    candidates.append(chunk)
                    candidate_indices.append(idx)
            else:
                candidates.append(chunk)
                candidate_indices.append(idx)
                
        if not candidates:
            candidates = self.chunks
            candidate_indices = list(range(len(self.chunks)))
            
        # 1. Compute TF-IDF Cosine Similarity
        query_vector = self.vectorizer.transform([query])
        candidate_tfidf = self.tfidf_matrix[candidate_indices]
        tfidf_scores = (candidate_tfidf * query_vector.T).toarray().flatten()
        
        # Apply keyword-based TF-IDF score boosting for rare FAQ target terms
        query_lower = query.lower()
        boost_terms = ["expense", "ratio", "exit", "load", "manage", "benchmark", "sip", "lock-in", "riskometer"]
        for i, chunk in enumerate(candidates):
            chunk_content_lower = chunk["content"].lower()
            boost = 1.0
            for term in boost_terms:
                if term in query_lower and term in chunk_content_lower:
                    boost += 0.5  # Boost by 50% for each matching rare FAQ term
            tfidf_scores[i] *= boost
        
        # 2. Compute Semantic Similarity if embeddings are available
        semantic_scores = None
        if self.embeddings is not None:
            try:
                response = genai.embed_content(
                    model="models/text-embedding-004",
                    contents=query
                )
                query_emb = self.normalize(np.array(response["embedding"]))
                candidate_embs = self.embeddings[candidate_indices]
                semantic_scores = np.dot(candidate_embs, query_emb)
            except Exception as e:
                print(f"Error during query embedding: {e}. Falling back to TF-IDF scores.")
                semantic_scores = None
                
        # 3. Combine scores (Hybrid Search)
        if semantic_scores is not None:
            # Hybrid: 30% TF-IDF, 70% Semantic
            hybrid_scores = 0.3 * tfidf_scores + 0.7 * semantic_scores
        else:
            # Fallback to TF-IDF only
            hybrid_scores = tfidf_scores
            
        # Sort candidates by score
        sorted_indices = np.argsort(hybrid_scores)[::-1]
        
        # Take the top matching chunks
        retrieved = []
        for rank in range(min(top_k, len(sorted_indices))):
            cand_idx = sorted_indices[rank]
            score = hybrid_scores[cand_idx]
            chunk = candidates[cand_idx].copy()
            chunk["score"] = float(score)
            chunk["tfidf_score"] = float(tfidf_scores[cand_idx])
            chunk["semantic_score"] = float(semantic_scores[cand_idx]) if semantic_scores is not None else 0.0
            retrieved.append(chunk)
            
        return retrieved

if __name__ == "__main__":
    # Test retrieval
    engine = RAGEngine()
    res = engine.retrieve("What is the exit load of Motilal Oswal Contra Fund?", top_k=2)
    print("\nTest Retrieval:")
    for r in res:
        print(f"Title: {r['title']} | Score: {r['score']:.4f} (TF-IDF: {r['tfidf_score']:.4f}, Semantic: {r['semantic_score']:.4f})")
        print(f"Content Preview: {r['content'][:150]}...\n")
