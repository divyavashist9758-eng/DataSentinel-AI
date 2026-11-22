from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from app.services.rag_engine import rag_engine
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/rag", tags=["RAG Incident Knowledge Base"])

class KnowledgeItemCreate(BaseModel):
    category: str
    title: str
    content: str
    recommended_action: str

@router.get("/search")
def search_knowledge(
    query: str = Query(..., min_length=2),
    category: Optional[str] = Query(None),
    top_k: int = Query(3, ge=1, le=10),
    current_user: User = Depends(get_current_user)
):
    """Retrieve historically verified incidents and remediation patterns matching query."""
    return rag_engine.retrieve_relevant_knowledge(query=query, category=category, top_k=top_k)

@router.get("/all")
def get_all_knowledge(current_user: User = Depends(get_current_user)):
    """List all indexed rules, incidents, and approved remediation runbooks."""
    return rag_engine.knowledge_items

@router.post("/index", status_code=status.HTTP_201_CREATED)
def index_knowledge_entry(
    entry: KnowledgeItemCreate,
    current_user: User = Depends(get_current_user)
):
    """Add a new incident postmortem or data quality rule to the RAG knowledge store."""
    entry_dict = entry.model_dump()
    rag_engine.add_knowledge_entry(entry_dict)
    return {"message": "Knowledge entry indexed successfully", "entry": entry_dict}
