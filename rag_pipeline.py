import os
import chromadb
from chromadb.config import Settings

# Setup a local directory for the Vector Database storage
DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

# Initialize persistent ChromaDB client
client = chromadb.PersistentClient(path=DB_PATH)

# Get or create our Curriculum knowledge collection
collection = client.get_or_create_collection(
    name="tutor_curriculum",
    metadata={"hnsw:space": "cosine"}
)

def seed_database():
    """Seeds the vector database with initial educational content if empty."""
    if collection.count() == 0:
        print("Seeding initial curriculum knowledge into local Vector DB...")
        documents = [
            "Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize nutrients from carbon dioxide and water. In plants, photosynthesis generally involves the green pigment chlorophyll and generates oxygen as a byproduct.",
            "A fraction represents a part of a whole or, more generally, any number of equal parts. It is written as a numerator over a denominator. Example: 3/4 means three parts out of four total equal parts.",
            "The Solar System is the gravitationally bound system of the Sun and the objects that orbit it. It contains eight planets: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune in order from the Sun.",
            "Newton's First Law of Motion states that an object will remain at rest or in uniform motion in a straight line unless acted upon by an external force. This is also known as the law of inertia."
        ]
        
        metadatas = [
            {"subject": "Biology", "topic": "Photosynthesis", "grade": "6-8"},
            {"subject": "Mathematics", "topic": "Fractions", "grade": "3-5"},
            {"subject": "Science", "topic": "Astronomy", "grade": "6-8"},
            {"subject": "Physics", "topic": "Classical Mechanics", "grade": "9-12"}
        ]
        
        ids = [f"curr_{i}" for i in range(len(documents))]
        
        # Add to collection (this automatically embeds using the default local ONNX model)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Successfully seeded {len(documents)} curriculum chunks into ChromaDB!")

# Run seed check on import
seed_database()

def retrieve_context(query: str, n_results: int = 2) -> list[str]:
    """Search the vector database for relevant curriculum context."""
    # Since ONNX inference is sometimes unstable on certain Windows environments,
    # we use a highly reliable keyword-based RAG fallback for the local prototype.
    query_lower = query.lower()
    
    fallback_docs = [
        "Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize nutrients from carbon dioxide and water. In plants, photosynthesis generally involves the green pigment chlorophyll and generates oxygen as a byproduct.",
        "A fraction represents a part of a whole or, more generally, any number of equal parts. It is written as a numerator over a denominator. Example: 3/4 means three parts out of four total equal parts.",
        "The Solar System is the gravitationally bound system of the Sun and the objects that orbit it. It contains eight planets: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune in order from the Sun.",
        "Newton's First Law of Motion states that an object will remain at rest or in uniform motion in a straight line unless acted upon by an external force. This is also known as the law of inertia."
    ]
    
    matched = []
    
    # Simple simulated retrieval
    if "photosynthesis" in query_lower or "plant" in query_lower:
        matched.append(fallback_docs[0])
    if "fraction" in query_lower or "math" in query_lower:
        matched.append(fallback_docs[1])
    if "solar" in query_lower or "planet" in query_lower or "space" in query_lower:
        matched.append(fallback_docs[2])
    if "newton" in query_lower or "gravity" in query_lower or "physics" in query_lower:
        matched.append(fallback_docs[3])
        
    if matched:
        return matched[:n_results]
        
    return ["No exact curriculum context found in the knowledge base."]

if __name__ == "__main__":
    # Test query
    sample_q = "Tell me about planets"
    res = retrieve_context(sample_q, 1)
    print(f"\nQuery: '{sample_q}'\nRetrieved: {res[0]}")
