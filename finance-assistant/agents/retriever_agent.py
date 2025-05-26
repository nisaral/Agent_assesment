from fastapi import FastAPI
from pydantic import BaseModel
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

app = FastAPI()
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = None

class RetrieverRequest(BaseModel):
    documents: list[str]
    query: str

@app.post("/retrieve")
async def retrieve(request: RetrieverRequest):
    global vector_store
    if not vector_store or request.documents:
        vector_store = FAISS.from_texts(request.documents, embeddings)
    results = vector_store.similarity_search_with_score(request.query, k=3)
    return [{"content": doc.page_content, "score": float(score)} for doc, score in results]