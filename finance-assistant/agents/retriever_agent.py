from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os
import logging
from .base_agent import create_base_app

app = create_base_app("Retriever Agent")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    logger.info("Successfully initialized embeddings model")
except Exception as e:
    logger.error(f"Failed to initialize embeddings model: {e}")
    embeddings = None

class RetrieveRequest(BaseModel):
    documents: list
    query: str

@app.post("/retrieve")
async def retrieve(request: RetrieveRequest):
    try:
        if not embeddings:
            raise ValueError("Embeddings model not initialized")
            
        if not request.documents:
            return {"results": [], "message": "No documents provided"}
            
        vectorstore = FAISS.from_texts(request.documents, embeddings)
        
        results = vectorstore.similarity_search_with_score(request.query, k=5)
        
        formatted_results = []
        for doc, score in results:
            try:
                embedding = embeddings.embed_query(doc.page_content)
                formatted_results.append({
                    "content": doc.page_content,
                    "score": float(score),
                    "embedding": embedding
                })
            except Exception as e:
                logger.warning(f"Error processing document: {e}")
                continue
                
        return formatted_results
        
    except Exception as e:
        logger.error(f"Retrieval error: {str(e)}")
        return {"error": f"Failed to process retrieval request: {str(e)}"}

@app.post("/run")
async def run(request: RetrieveRequest):
    return await retrieve(request)