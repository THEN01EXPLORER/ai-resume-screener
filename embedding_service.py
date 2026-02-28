import chromadb
from chromadb.utils import embedding_functions
chroma_client = chromadb.PersistentClient(path = "./chroma_db")

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name = "resumes",
    embedding_function = sentence_transformer_ef
)

def add_resume_to_db(filename: str, text: str, skills: list, experience: float):
    """
    Stores the resume text and structured metadata into the Vector DB.
    """
    skills_text = ", ".join(skills)
    full_searchable_text = f"{text}\n\nKeywords: {skills_text}"
    
    collection.upsert(
        documents=[full_searchable_text],
        metadatas=[{
            "filename": filename, 
            "skills": skills_text,
            "experience": experience
        }],
        ids=[filename]
    )


def query_resumes(query_text: str, n_results=5):
    """
    Searches the database for resumes that match the query semantically.
    """
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    return results


def get_resume_count() -> int:
    """
    Returns the total number of resumes stored in the Vector DB.
    """
    return collection.count()